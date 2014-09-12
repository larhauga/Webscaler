#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python program for scaling webservices with HAproxy
from bin import haproxy, hastats
from bin.nova import openstack
import time
import datetime

backends = []
min_backends = 2
previously = []
# server_threshold = 20
# needed_backends =
# actions on the way

# figure out how to get the difference and keep count

def scale_up():
    stack = openstack()
    new = None
    sleeping = stack.sleeping_machine()
    if sleeping:
        new = sleeping
        new.start()
    else:
        new = stack.create_backend()


    #ha = haproxy.HAproxy()

    # nova create server
    # get information
    # haproxy add server
    pass

def scale_down():
    ha = haproxy.HAproxy()
    stack = openstack()
    #backends = stack.backends()

    # haproxy set offline
    # wait untill no more connections
    # nova remove server
    pass

def what_do():
    # get current cumulative request counter
    current = hastats.get_backend_cum_requests()['stot']
    # check what is normal
    difference = 0
    if previously:
        difference = int(current) - int(previously[-1])
    print difference
    # devided by the nodes?
    backends = hastats.get_stat_backends()

    print difference / len(backends)

    previously.append(current)

    print "Cum connections on backend: %s" % str(current)
    print "Total backends: %s" % str(len(backends))


def update_conf():
    """ Do we need to update the configuration? """
    stats = hastats.get_stat_backends()
    stack = openstack()
    backends = stack.backends()
    if not len(backends) == len(stats):
        print "inside"
        ha = haproxy.HAproxy()
        ha.compile(backends)
        ha.restart()

def main():
    conns = []
    try:
        while True:
            first = datetime.datetime.now()
            for line in hastats.get_stat_backends():
                print line['svname'] + ', ' + line['status']
            what_do()
            update_conf()
            c =  datetime.datetime.now() - first
            print c.seconds
            print c
            second = datetime.datetime.now()
            time.sleep(10)
            d = datetime.datetime.now() - second
            print d.seconds
            print d

            # getstat check 'rate'
        # while testing connections
            # check difference
            # scale up / scale down

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
