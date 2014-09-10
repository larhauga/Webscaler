#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python program for scaling webservices with HAproxy
from haproxy import haproxy
from nova import openstack

backends = []
min_backends = 2

# figure out how to get the difference and keep count

def scale_up():
    stack = openstack()
    sleeping = stack.sleeping_machine()
    if sleeping:
        sleeping.start()
    else:
        new_instance = stack.create_backend()


    ha = haproxy.HAproxy()

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
    pass

def main():
    # while testing connections
        # check difference
        # scale up / scale down

    stack = openstack()
    ha = haproxy.HAproxy()

    ha.compile(stack.active_backends())
    ha.restart()

if __name__ == '__main__':
    main()
