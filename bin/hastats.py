#!/usr/bin/env python
# -*- coding: utf-8 -*-

from haconn import HAconn
import pprint

def get_info():
    con = HAconn()
    data = con.send_cmd('show info\r\n')
    con.close()

    return dict([ line.split(': ') for line in data.splitlines() if line])

def get_stat(output=None):
    con = HAconn()
    data = con.send_cmd('show stat\r\n')

    lines = data.splitlines()
    header = lines.pop(0).split('# ')[1].split(',')
    #print header
    l = []
    for line in lines:
        if len(line.split(',')) > 1:
            l.append(dict(zip(header, line.split(','))))
    con.close()

    if output:
        s = ''
        for key, value in l[0].iteritems():
            s += 'key (%s)' % key
            for i in l:
                if key and len(i) > 1:
                    s += i[key] + ','
            s += '\n'
        print s

    return l

def get_stat_backends():
    stats = get_stat()
    backends = []
    for node in stats:
        if 'node' in node['svname']:
            backends.append(node)

    return backends

def get_backend_cum_requests():
    stats = get_stat()
    for node in stats:
        if 'nodes' in node['pxname'] and 'BACKEND' in node['svname']:
            return node

def cum_req():
    pass

def previous_req():
    pass

def main():
    #print get_info()
    #print get_cur_req()
    get_stat(output=True)

if __name__ == '__main__':
    main()
