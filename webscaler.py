#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python program for scaling webservices with HAproxy
from bin import haproxy, hastats
from bin.nova import openstack
from math import ceil
import time
import datetime
import csv

sleeptime = 60
min_backends = 2
server_threshold = 10
current_backends = 0
pending_backends = []
quota_limit = 13

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
def write_data():
    with open('%s-webscaler' % (datetime.datetime.now().strftime("%Y-%m-%dT%H%M")), 'wb') as f:
        w = csv.DictWriter(f, metrics[0].keys)
        header = metrics[0].keys()
        #header = sorted([k for k, v in metrics[0].items()])
        csv_data = [header]
        for d in metrics:
            csv_data.append([d[h] for h in header])
        w.writer.writerows(csv_data)


def scale_up(Number=1):
    stack = openstack()
    sleeping = stack.sleeping_machine()

    if len(stack.backends()) == (quota_limit-1):
        return False

    scaled = 0
    if sleeping:
        print sleeping
        #if not 'powering-on' in sleeping.state:
        sleeping.start()
        scaled += 1
    else:
        if scaled < Number:
            instances = []
            for i in range(0,Number-scaled):
                instances.append(stack.create_backend())
            return instances


    # could reload proxy here?

def scale_down(Number=1):
    ha = haproxy.HAproxy()
    stack = openstack()
    active = stack.active_backends()
    passive = stack.passive_backends()
    instance = None

    print "active servs: %s, min bakends: %s" % (str(len(active)), str(min_backends))

    if len(active) <= min_backends:
        return False
    print passive
    print active

    removed = 0

    if passive:
        for node in passive:
            print "Removing passive node %s" % node.name
            node.delete()
            removed += 1

    if not passive and len(active) == (min_backends+1):
        active[-i].stop()
        return True

    if active:
        left = len(active) - min_backends - (Number-removed)
        if left > min_backends:
            toremove = Number-removed
            for i in range(0,toremove):
                print "Stopping node %s" % active[-1].name
                active[-1].stop()

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
    time.sleep(sleeptime)
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

def new_metrics(current_cumulated, hareset=False):
    current = {}
    current['acu'] = current_cumulated
    current['date'] = datetime.datetime.now()
    current['diff'] = (float(current_cumulated) - float(metrics[-1]['acu'])) \
            / float((current['date']-metrics[-1]['date']).seconds)
    current['needed'] = needed_servers(acu=current['acu'], diff=current['diff'])

    current['active'] = len(hastats.get_backends_up())

    if hareset:
        current['acu'] = 0
        current['diff'] = metrics[-1]['diff']
        current['needed'] = metrics[-1]['needed']

    #stack = openstack()
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
            time.sleep(sleeptime)
            current = new_metrics(hastats.get_backend_cum_requests()['stot'])
            print metrics
            print needed_servers()

            # What to do? Scale up/down or are we happy?
            stack = openstack()
            active_backends = stack.active_backends()
            up_backends = hastats.get_backends_up()

            needed = needed_servers()
            #if len(active_backends) == len(up_backends):
                # We are in concurrency
            if needed > len(active_backends):
                print "Scaling up"
                scale_up(needed-len(active_backends))
            elif needed < len(active_backends):
                print "Scaling down"
                if not scale_down(len(active_backends)-needed):
                    print "Lowest number"
            else:
                # Sleeping
                print "Sleeping one more round"

            update_conf()
            new_metrics(0, hareset=True)

            for line in hastats.get_stat_backends():
                print line['svname'] + ', ' + line['status']

            time.sleep(sleeptime)

    except KeyboardInterrupt:
        write_data()
        pass

if __name__ == '__main__':
    main()
