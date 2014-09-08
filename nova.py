#!/usr/bin/env python
# -*- coding: utf-8 -*-

from novaclient import client
from os import environ, path
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
        """ Get the virtual machines that are backends """
        nodes = self.nova.servers.list()
        backends = []

        for node in nodes:
            if "node" in node.name:
                backends.append(node)

        #print backends
        #print dir(backends[0])
        #print backends[0].addresses
        #print backends[0].to_dict()
        #print backends[0].addresses
        return backends
        #print nodes
        #print dir(nodes[0])
        #print nodes[0].to_dict()
        #print nodes[0].addresses
        #for node in nodes:
            #print node

    def get_status(self):
        """ Get the machine status """
        pass

    def get_info(self):
        """ Get information of a instnace.
            Returns: Dict with at least IP if present
        """
        pass

    def create_web(self):
        """ Creates a instance in Openstack """
        pass

    def terminate(self,machine):
        """ Terminates a instance """
        pass

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

