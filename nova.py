#!/usr/bin/env python
# -*- coding: utf-8 -*-

from novaclient import client, v1_1
from os import environ, path
import time
import ConfigParser

class openstack:

    def __init__(self):
        p = path.dirname(path.abspath(__file__))
        p = path.join(p, 'etc/openstack.cfg')
        if path.isfile(p):
            config = ConfigParser.ConfigParser()
            config.read(p)
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

    def backends(self):
        """ Get the virtual machines that are backends
            Returns: List of server objects
        """
        nodes = self.nova.servers.list()
        backends = []

        for node in nodes:
            if "node" in node.name:
                backends.append(node)

        return backends

    def get_status(self):
        """ Get the machine status """
        pass

    def get_info(self):
        """ Get information of a instnace.
            Returns: Dict with at least IP if present
        """
        pass

    def create_backend(self):
        """ Creates a instance in Openstack """
        keypair = self.nova.keypairs.find(name='hlarshaugan')
        image = self.nova.images.find(name='ubuntu-12.04')
        flavor = self.nova.flavors.find(name='m1.medium')
        net = self.nova.networks.find(label='MS016A_net')
        nics = [{"net-id": net.id, "v4-fixed-ip": ''}]

        server = self.nova.servers.create(name = 'node',
                                    image = image.id,
                                    flavor = flavor.id,
                                    nics = nics,
                                    key_name = keypair.name)

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
        if isinstance(instance, v1_1.servers.Server):
            instance.stop()
        else:
            self.nova.servers.findall(name=instance)[0].stopp()

    def delete(self, instance):
        """ Terminates a instance """
        if isinstance(instance, v1_1.servers.Server):
            instance.delete()
        else:
            self.nova.servers.findall(name=instance)[0].delete()

def main():
    stack = openstack()
    stack.backends()
    #print stack.cred

    #nova = client.Client(**stack.cred)
    #print nova.flavors.list()
    #print nova.servers.list()[0].status
    #print nova.servers.list()[0].addresses
    #print nova.limits.get().to_dict()
    #print nova.quotas.get('59a46c9fcf174ec3890211cc86e0836b', user_id='s171201').instances

if __name__ == '__main__':
    main()

