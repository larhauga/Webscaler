#!/usr/bin/env python
# -*- coding: utf-8 -*-

from novaclient import client, v1_1
from os import environ, path
import time
import ConfigParser

class openstack:

    def __init__(self):
        self.p = path.split(path.dirname(path.abspath(__file__)))[0]
        opens = path.join(self.p, 'etc/openstack.cfg')
        if path.isfile(opens):
            config = ConfigParser.ConfigParser()
            config.read(opens)
        else:
            logging.error("Missing configuration file 'etc/openstack.cfg'")
            exit(1)

        self.cred = {}
        self.cred['version'] = config.get('main', 'API_VERSION')
        self.cred['username'] = config.get('main', 'USERNAME')
        self.cred['api_key'] = config.get('main', 'PASSWORD')
        self.cred['auth_url'] = config.get('main', 'AUTH_URL')
        self.cred['project_id'] = config.get('main', 'TENANT_NAME')

        self.nova = client.Client(**self.cred)

    def reload_conf(self):
        self.__init__(self)

    def backends(self):
        """ Get the virtual machines that are backends
            Returns: List of server objects
        """
        nodes = self.nova.servers.list()
        backends = []

        for node in nodes:
            if "node" in node.name:
                backends.append(node)

        return backends[::-1]

    def active_backends(self):
        active = []
        for node in self.backends():
            if node.status in 'ACTIVE':
                active.append(node)

        return active

    def passive_backends(self):
        passive = []
        for node in self.backends():
            if not node.status in 'ACTIVE':
                passive.append(node)
        return passive


    def create_backend(self):
        """ Creates a instance in Openstack """
        backends = self.backends()

        name = 'node-%s' % str(self.get_instance_number(nodes=backends, next=True))

        keypair = self.nova.keypairs.find(name='hlarshaugan')
        image = self.nova.images.find(name='ubuntu-12.04')
        #flavor = self.nova.flavors.find(name='m1.medium')
        flavor = self.nova.flavors.find(name='m1.tiny')
        net = self.nova.networks.find(label='MS016A_net')
        nics = [{"net-id": net.id, "v4-fixed-ip": ''}]
        f = open(path.join(self.p, 'etc/clouddata.txt'), 'r')

        # try/except novaclient.exceptions.OverLimit
        server = self.nova.servers.create(name = name,
                                    image = image.id,
                                    flavor = flavor.id,
                                    nics = nics,
                                    key_name = keypair.name,
                                    userdata=f)

        status = server.status
        while status == 'BUILD':
            time.sleep(5)
            instance = self.nova.servers.get(server.id)
            status = instance.status

        return instance

    def start(self, instance):
        if isinstance(instance, v1_1.servers.Server):
            instance.start()
        else:
            self.nova.servers.findall(name=instance)[0].start()

    def shutdown(self, instance):
        if not instance:
            return False
        if isinstance(instance, v1_1.servers.Server):
            instance.stop()
        else:
            self.nova.servers.find(name=instance).stop()

    def delete(self, instance):
        """ Terminates a instance """
        if isinstance(instance, v1_1.servers.Server):
            instance.delete()
        else:
            self.nova.servers.findall(name=instance)[0].delete()

    def get_instance_number(self, nodes=None, next=False,lowest=False):
        if not nodes:
            nodes = self.backends()
        numbers = []
        for node in nodes:
            numbers.append(int(node.name.split('-')[1]))

        if next:
            if numbers:
                return max(numbers) + 1
            else:
                return 1
        elif lowest:
            return min(numbers)
        else:
            return numbers

    def sleeping_machine(self):
        """ Returns the first shutoff machine """
        backends = self.backends()
        for node in backends:
            if node.status in 'SHUTOFF':
                return node
        return None

def main():
    stack = openstack()
    print stack.backends()
    print stack.create_backend()

    #print nova.limits.get().to_dict()
    #print nova.quotas.get('59a46c9fcf174ec3890211cc86e0836b', user_id='s171201').instances

if __name__ == '__main__':
    main()

