#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import socket, AF_UNIX, SOCK_STREAM
from haproxy import const

HA_BUFSIZE = 8192

class HAconn(self, sockfile):
    def __init__(self, sockfile):
        self.sockfile = sockfile
        self.sock = None
        self.open()

    def open(self):
        self.sock = socket(AF_UNIX, SOCK_STREAM)
        self.sock.connect(self.sockfile)

    def send_cmd(self, cmd, objectify=False):
        """Receives a command obj and sends it to the
           socket. Receives the output and passes it through
           the command to parse it a present it.
           - objectify -> Return an object instead of plain text"""

        res = ""
        self.sock.send(cmd.getCmd())
        output = self.sock.recv(HA_BUFSIZE)

        while output:
            res += output
            output = self.sock.recv(const.HaP_BUFSIZE)

        if objectify:
            return cmd.getResultObj(res)

        return cmd.getResult(res)

    def close(self):
        """Closes the socket"""
        self.sock.close()

def main():
    con = HAcon('/var/run/haproxy/admin.sock')

if __name__ == '__main__':
    main()
