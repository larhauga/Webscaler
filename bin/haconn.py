#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import socket, AF_UNIX, SOCK_STREAM
#from haproxy import const

HA_BUFSIZE = 8192

class HAconn:
    def __init__(self, sockfile=None):
        if not sockfile:
            self.sockfile = '/var/run/haproxy/admin.sock'
        else:
            self.sockfile = sockfile
        self.sock = None
        self.open()

    def open(self):
        self.sock = socket(AF_UNIX, SOCK_STREAM)
        self.sock.connect(self.sockfile)

    def send_cmd(self, cmd):

        res = ""
        self.sock.send(cmd)
        output = self.sock.recv(HA_BUFSIZE)

        while output:
            res += output
            output = self.sock.recv(HA_BUFSIZE)

        return res

    def close(self):
        """Closes the socket"""
        self.sock.close()

def main():
    #con = HAconn('/var/run/haproxy/admin.sock')
    ##print con.send_cmd('show stat\r\n')
    #print con.send_cmd('enable server nodes/node02\r\n')
    #con.close()
    con = HAconn()
    print con.send_cmd('show info\r\n')
    con.close()
    con = HAconn()
    print con.send_cmd('show stat\r\n')
    con.close()
    con = HAconn()
    print con.send_cmd('show sess\r\n')
    con.close()
    con = HAconn()
    print con.send_cmd('show table\r\n')
    con.close()

if __name__ == '__main__':
    main()
