#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen
from conn import HAconn

socket = "/var/run/haproxy/admin.sock"

def restart():
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

def compile():
    pass

def set_online(host):
    conn = HAconn(socket)
    send_cmd()
    pass

def set_offline(host):
    pass


def main():
    print restart()

if __name__ == '__main__':
    main()
