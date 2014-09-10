#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conn import HAconn
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
        l.append(dict(zip(header, line.split(','))))
    con.close()

    #pprint.pprint(l)
    if output:
        for key, value in l[0].iteritems():
            print "key (%s): %s, %s, %s, %s" % (key, value, l[1][key], l[2][key], l[3][key])

    return l


def get_cur_req():
    return get_info()['CumConns']

def cum_req():
    pass


def previous_req():
    pass

def main():
    #print get_info()
    #print get_cur_req()
    print get_stat(output=True)

if __name__ == '__main__':
    main()
