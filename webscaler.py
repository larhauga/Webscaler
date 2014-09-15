#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python program for scaling webservices with HAproxy
from bin import haproxy, hastats
from bin.nova import openstack
from math import ceil
import time
import datetime

sleeptime = 60
min_backends = 2
server_threshold = 10
current_backends = 0
pending_backends = 0

metrics = []
actions = {}
# actions on the way

# figure out how to get the difference and keep count
"""
    What data do we need in metrics?
    date: date object of when
    acu: accumulated requests
    diff: difference since last time

"""

def scale_up():
    stack = openstack()
    sleeping = stack.sleeping_machine()
    if sleeping:
        sleeping[0].start()
    else:
        return stack.create_backend()

    # could reload proxy here?


def scale_down():
    ha = haproxy.HAproxy()
    stack = openstack()
    active = stack.active_backends()
    passive = stack.passive_backends()
    instance = None

    print "active servs: %s, min bakends: %s" % (str(len(active)), str(min_backends))

    return True

    # haproxy set offline
    # wait untill no more connections
    # nova remove server

def what_do():
    # get current cumulative request counter
    current = hastats.get_backend_cum_requests()['stot']

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

def initiate():
    # Gathering first data
    data = {}
    data['acu'] = hastats.get_backend_cum_requests()['stot']
    data['diff'] = 0
    data['date'] = datetime.datetime.now()
    data['active'] = len(hastats.get_backends_up())
    data['needed'] = None
    metrics.append(data)
    print metrics
    time.sleep(2)
    last = data
    data = {}
    data['acu'] = hastats.get_backend_cum_requests()['stot']
    data['diff'] = (float(data['acu']) - float(last['acu'])) / float(sleeptime)
    data['date'] = datetime.datetime.now()
    data['needed'] = needed_servers(acu=data['acu'], diff=data['diff'])
    data['active'] = len(hastats.get_backends_up())
    metrics.append(data)

def needed_servers(acu=None,diff=None):
    last = metrics[-1]
    # calculate servers for the load
    # requests per sec / threshold
    # ceil: rounds up
    needed = int(ceil(float(last['diff']) / float(server_threshold)))
    return needed

def new_metrics(current_cumulated):
    current = {}
    current['acu'] = current_cumulated
    current['diff'] = (float(current_cumulated) - float(metrics[-1]['acu'])) / float(sleeptime)
    current['date'] = datetime.datetime.now()
    current['needed'] = needed_servers(acu=current['acu'], diff=current['diff'])

    #stack = openstack()
    current['active'] = len(hastats.get_backends_up())
    #current['active'] = stack.active_backends()

    metrics.append(current)
    return current

    ######
    # NOTE! HANDLE RESTART!!!
    ######

def main():
    # Starting the first time
    # getting current cum connections

    try:

        if not metrics:
            print("Gathering initial data...")

            # Gathering first data
            initiate()

        while True:
            current = new_metrics(hastats.get_backend_cum_requests()['stot'])
            print metrics
            print needed_servers()

            for line in hastats.get_stat_backends():
                print line['svname'] + ', ' + line['status']

            time.sleep(sleeptime)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
