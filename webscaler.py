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
server_threshold = 20
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

    # could reload proxy here?


def scale_down():
    ha = haproxy.HAproxy()
    stack = openstack()
    active = stack.active_backends()
    passive = stack.passive_backends()
    instance = None

    print "active servs: %s, min bakends: %s" % (str(len(active)), str(min_backends))
    if (len(active)) == min_backends:
        if len(passive) == 0:
            return False
    if not passive:
        if active:
            instance = active.pop()
            ha.set_offline(instance.name)
            #time.sleep(10)
            stack.shutdown(instance)
    else:
        for node in passive:
            stack.delete(node)
            instance = active[-1]
            ha.set_offline(instance.name)
        stack.shutdown(instance)

    return True

    # haproxy set offline
    # wait untill no more connections
    # nova remove server

def what_do():
    # get current cumulative request counter
    current = hastats.get_backend_cum_requests()['stot']
    # check what is normal
    difference = 0
    if previously:
        if previously[-1] > current:
            difference = current
        else:
            difference = int(current) - int(previously[-1])
    else:
        difference = current

    # devided by the nodes?
    backends = hastats.get_stat_backends()

    capacity = server_threshold * len(backends)
    print "capacity: %s, difference: %s" % (str(capacity), str(difference))
    if capacity < difference:
        print "Im scaling up! Not doing this alone"
        if scale_up():
            print "Launched new instance"
    elif capacity > difference:
        if int(min_backends) == int(len(backends)):
            return
        elif scale_down():
            print "Scaled down"
        else:
            print "Not scaling down. Possible no more hosts to remove"
    else:
        print "Im dooing nothing!"

    print int(difference) / int(len(backends))

    previously.append(current)

    print "Cum connections on backend: %s" % str(current)
    print "Total backends: %s" % str(len(backends))


def update_conf():
    """ Do we need to update the configuration? """
    stats = hastats.get_stat_backends()
    stack = openstack()
    backends = stack.backends()
    if not len(backends) == len(stats):
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
            #c =  datetime.datetime.now() - first
            #print c.seconds
            #print c
            #second = datetime.datetime.now()
            time.sleep(10)
            #d = datetime.datetime.now() - second
            #print d.seconds
            #print d

            # getstat check 'rate'
        # while testing connections
            # check difference
            # scale up / scale down

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
