#!/usr/bin/env python
# -*- coding: utf-8 -*-

from novaclient import client
from os import environ,path
import ConfigParser


class openstack:

    def __init__(self):
        if path.isfile('etc/openstack.cfg'):
            config = ConfigParser.ConfigParser()
            config.read('etc/openstack.cfg')
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

    #def get_nova_creds():
        #c = {}
        #c['version'] = '2'
        #c['username'] = environ['OS_USERNAME']
        #c['api_key'] = environ['OS_PASSWORD']
        #c['auth_url'] = environ['OS_AUTH_URL']
        #c['project_id'] = environ['OS_TENANT_NAME']
        #return c

    def get_backends():
        """ Get the virtual machines that are backends """
        pass

    def get_status():
        pass

    #creds = get_nova_creds()
    #nova = client.Client(**creds)
    #print nova.flavors.list()
    #print nova.servers.list()[0].status
    #print nova.servers.list()[0].addresses
    #print nova.limits.get().to_dict()
    #print nova.quotas.get('59a46c9fcf174ec3890211cc86e0836b', user_id='s171201').instances

    def create_web():
        pass

    def terminate():
        pass

def main():
    stack = openstack()
    print stack.cred

    #creds = get_nova_creds()
    nova = client.Client(**stack.cred)
    print nova.flavors.list()
    print nova.servers.list()[0].status
    print nova.servers.list()[0].addresses
    print nova.limits.get().to_dict()

if __name__ == '__main__':
    main()

