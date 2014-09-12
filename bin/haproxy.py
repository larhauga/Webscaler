#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from haconn import HAconn
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

        # Example
        # nodes=[ {'name': 'node01', 'ip': '192.168.128.48','id':1},]
        with open('/etc/haproxy/haproxy.cfg', 'wb') as f:
            f.write(template.render(nodes=nodes))

    def set_online(self, instancename):
        conn = HAconn()
        ret = conn.send_cmd('enable server nodes/%s' % (instancename))
        conn.close()
        return ret

    def set_offline(self,instancename):
        conn = HAconn()
        ret = conn.send_cmd('disable server nodes/%s' % (instancename))
        conn.close()
        return ret


def main():
    ha = HAproxy()
    ha.compile()

if __name__ == '__main__':
    main()
