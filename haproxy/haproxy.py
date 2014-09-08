#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen
#from conn import HAconn
from os import path
from jinja2 import Environment, PackageLoader, FileSystemLoader

socket = "/var/run/haproxy/admin.sock"
class HAproxy:
    def __init__(self):
        self.subnet = 'MS016A_net'
        pass

    def restart(self):
        """ """
        # Need to collect the current sessions before restart!
        # service haproxy reload # < will reload the config with minimal service impact
        # Needs to be run with root privileges
        pr = subprocess.Popen("service haproxy reload".split(), stdout=subprocess.PIPE)
        output, err = pr.communicate()

        if not err:
            return True
        else:
            return False

    def compile(self, serverlist):
        #http://jinja.pocoo.org/docs/dev/api/
        p = path.dirname(path.abspath(__file__))
        env = Environment(loader=FileSystemLoader(path.split(p)[0] + '/etc/'))
        template = env.get_template('haproxy.cfg')

        nodes = []
        counter = 1
        for server in serverlist:
            s = {}
            s['name'] = server.name
            s['ip'] = server.addresses[self.subnet][0]['addr']
            s['id'] = counter
            counter += 1
            nodes.append(s)

        #nodes=[ {'name': 'node01', 'ip': '192.168.128.48','id':1},
                #{'name': 'node02', 'ip': '192.168.128.50','id':2},
                #{'name': 'node03', 'ip': '192.168.128.51','id':3}]
        print template.render(nodes=nodes)


    def set_online(self,host):
        conn = HAconn(socket)
        send_cmd()
        pass

    def set_offline(self,host):
        pass


def main():
    ha = HAproxy()
    ha.compile()

if __name__ == '__main__':
    main()
