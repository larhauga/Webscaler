#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python program for scaling webservices with HAproxy
from bin import haproxy, hastats
from bin.nova import openstack
from math import ceil
from threading import Thread, Lock
import time
import datetime
import csv

import sys, traceback

sleeptime = 60
min_backends = 2
server_threshold = 10
current_backends = 0
pending_backends = []
quota_limit = 13
ha_reloaded = False
ha_last_reload = None
epoch_start = datetime.datetime.now()

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

    if len(stack.backends()) == (quota_limit):
        return False

    scaled = 0
    if sleeping:
        print sleeping
        if len(sleeping) > 1:
            for node in sleeping:
                if scaled < Number: # and not 'powering-on' in node.state:
                    node.start()
                    scaled += 1
        else:
            if not 'ACTIVE' in sleeping[0].status:
                sleeping[0].start()
                scaled += 1

    else:
        if scaled < Number:
            thread = Thread(target=stack.create_multiple(Number-scaled))
            thread.start()

def scale_down(Needed=1):
    ha = haproxy.HAproxy()
    stack = openstack()
    active = stack.active_backends()
    passive = stack.passive_backends()
    instance = None

    print "active servs: %s, min bakends: %s, needed: %s" % (str(len(active)), str(min_backends), str(Needed))
    toremove = len(active) - Needed
    removed = 0
    threads = []
    #print passive
    #print active
    if len(passive) > 1:
        # Delete the stopped nodes, and leave one
        for node in passive[1:][::-1]:
            handle_scaledown(node, delete=True)

    if toremove > 0:
        print "Want to remove %s nodes" % str(toremove)
        if len(active) <= min_backends:
            return False
        elif (len(active) - toremove) > min_backends:
            for i in range(1, toremove + 1):
                if 'ACTIVE' in active[-i].status:
                    handle_scaledown(active[-i], stop=True)
        else:
            recalculate = len(active) - (Needed + min_backends)
            for i in range(1, recalculate+1):
                if 'ACTIVE' in active[-i].status:
                    handle_scaledown(active[-i], stop=True)

    else:
        print "No nodes to stop/delete"
        return False
        #if not threads:
            #return False

    #if len(active) <= min_backends:
        #if passive > 1:
            #for node in passive:
                #node.delete()
            #return True
        #return False
    #for thread in threads:
        #print "Starting thread"
        #thread.start()
        #thread.join()

    #for thread in threads:
        #thread.join()

    #if passive:
        #for node in passive:
            #print "Removing passive node %s" % node.name
            #node.delete()
            #removed += 1

    #if not passive and len(active) == (min_backends+1):
        #print "Stopping node %s" % active[-1].name
        #active[-1].stop()
        #return True

    #if active:
        #print "Starting to remove active nodes, wanting to remove %s nodes" % Number
        #left = len(active) - (Number-removed)
        #toremove = Number - removed #- (min_backends)

        #print "Number that will be left: %s" % str(left)
        #if left > min_backends:
            #print "Ok, so we are removing: %s hosts" % str(toremove)
            #for i in range(1,toremove):
                #print "Iteration %s" % str(i)
                #if 'ACTIVE' in active[-i].status:
                    #print "Stopping node %s" % active[-i].name
                    #active[-i].stop()
                #elif 'SHUTOFF' in active[-i].status:
                    #print "Deleting node &s" % active[-i].name
                    #active[-i].delete()
        #elif left <= min_backends:
            #stack = openstack()
            #b = stack.backends()
            #remove = len(b) - min_backends
            #for i in range(1, remove+1):
                #if 'ACTIVE' in active[-i].status:
                    #print "Stopping node %s" % active[-i].name
                    #active[-i].stop()
                #else:
                    #print "Not removing %s since it is %s" % (active[-i].name, active[-i].status)

    return True

def handle_scaledown(instance, delete=False, stop=False):
    print "Starting to handle scaledown of %s" % instance.name
    ha = haproxy.HAproxy()
    stack = openstack()
    # Set the instance in draining mode.
    # No new conns. Active finishes
    ha.drain(instance)
    # Operating with short draintime (only static page)
    time.sleep(1)
    try:
        if stop:
            print "Stopping node %s" % instance.name
            instance.stop()
        elif delete:
            print "Deleting node %s" % instance.name
            instance.delete()
    except:
        print "Cant stop/delete instnace %s" % instance.name
        traceback.print_exc(file=sys.stdout)



def update_conf():
    """ Do we need to update the configuration? """
    global ha_reloaded
    stats = hastats.get_stat_backends()
    stack = openstack()
    backends = stack.backends()
    if not len(backends) == len(stats):
        ha = haproxy.HAproxy()
        ha.compile(backends)
        global ha_last_reload
        ha_last_reload = datetime.datetime.now()
        if ha.restart():
            ha_reloaded = True
        return True
    return False

def initiate():
    # Boot first machines if not active:
    stack = openstack()
    backends = stack.backends()
    #if len(backends) < min_backends:
        #scale_up(min_backends)
    # Gathering first data
    data = {}
    data['acu'] = hastats.get_backend_cum_requests()['stot']
    data['diff'] = 0
    data['diffpt'] = 0
    data['date'] = datetime.datetime.now()
    data['active'] = len(stack.active_backends())#len(hastats.get_backends_up())
    data['haactive'] = len(hastats.get_backends_up())
    data['needed'] = None
    data['epoch'] = (datetime.datetime.now()-epoch_start).seconds
    metrics.append(data)
    print metrics
    time.sleep(sleeptime)
    last = data
    data = {}
    data['acu'] = hastats.get_backend_cum_requests()['stot']
    data['diff'] = int((float(data['acu']) - float(last['acu'])) / float(sleeptime))
    data['diffpt'] = data['diff'] * sleeptime
    data['date'] = datetime.datetime.now()
    data['needed'] = needed_servers(acu=data['acu'], diff=data['diff'])
    data['active'] = len(stack.active_backends())#len(hastats.get_backends_up())
    data['haactive'] = len(hastats.get_backends_up())
    data['epoch'] = (datetime.datetime.now()-epoch_start).seconds
    metrics.append(data)
    time.sleep(sleeptime)

def needed_servers(acu=None,diff=None):
    last = metrics[-1]
    # calculate servers for the load
    # requests per sec / threshold
    # ceil: rounds up
    #needed = int(ceil(float(last['diff']) / float(server_threshold)))
    print diff
    needed = int(ceil(int(diff) / float(server_threshold)))
    return needed

def new_metrics(current_cumulated, hareset=False):
    global ha_reloaded
    global ha_last_reload
    current = {}
    current['acu'] = current_cumulated
    current['date'] = datetime.datetime.now()

    if ha_reloaded:
        last_cumulated = 0
        difference = int(ceil((float(current_cumulated) - float(last_cumulated)) \
                / float((current['date'] - ha_last_reload).seconds)))
        diffpt = int(difference) * (current['date'] - ha_last_reload).seconds

    try:
        print "Current new cumulated connections: %s" % str(current_cumulated)
        print "Calculation: float(%s) - float(%s) / float(%s-%s.seconds (%s))" % \
                (str(current_cumulated), metrics[-1]['acu'], str(current['date']), str(metrics[-1]['date']),\
                str((current['date'] - metrics[-1]['date']).seconds))

        if ha_reloaded:
            current['diff'] = difference
            current['diffpt'] = diffpt
            ha_reloaded = False
        else:
            current['diff'] = int(ceil((float(current_cumulated) - float(metrics[-1]['acu'])) \
                    / float((current['date']-metrics[-1]['date']).seconds)))
            current['diffpt'] = current['diff'] * (current['date']-metrics[-1]['date']).seconds
        #else:
            #current['diff'] = 0
    except ZeroDivisionError:
        current['diff'] = 0

    stack = openstack()
    current['needed'] = needed_servers(acu=current['acu'], diff=current['diff'])
    current['active'] = len(stack.active_backends())#len(hastats.get_backends_up())
    current['haactive'] = len(hastats.get_backends_up())
    current['epoch'] = (datetime.datetime.now()-epoch_start).seconds

    #if hareset:
        #current['acu'] = current_cumulated
        #current['diff'] = metrics[-1]['diff']
        #current['needed'] = needed_servers(acu=current['acu'], diff=current['diff'])

    #stack = openstack()
    #current['active'] = stack.active_backends()

    metrics.append(current)
    return current

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
            print metrics[-1]
            print "Needed servers: %s" % str(needed_servers(diff=current['diff']))

            # What to do? Scale up/down or are we happy?
            stack = openstack()
            active_backends = stack.active_backends()
            up_backends = hastats.get_backends_up()

            needed = needed_servers(diff=current['diff'])
            #if len(active_backends) == len(up_backends):
                # We are in concurrency
            if needed > len(active_backends):
                print "Scaling up"
                scale_up(needed-len(active_backends))
            elif needed < len(active_backends):
                print "Scaling down"
                if not scale_down(Needed=needed):#len(active_backends)-needed):
                    print "Lowest number"
            else:
                # Sleeping
                print "Sleeping one more round"

            if update_conf():
                print "HAproxy config reloaded"
                print ha_last_reload
            #new_metrics(hastats.get_backend_cum_requests()['stot'], hareset=True)

            for line in hastats.get_stat_backends():
                print line['svname'] + ', ' + line['status']

            time.sleep(sleeptime)

    except KeyboardInterrupt:
        write_data()
        pass

if __name__ == '__main__':
    main()
