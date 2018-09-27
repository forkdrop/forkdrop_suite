# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import socket
import ssl
import json
import sys

import lib.third_party.socks as socks

from lib.utl.print import print_red, chill_yellow_str, chill_green_str
from lib.utl.dir_manager import DirectoryManager
from lib.utl.file_manager import FileManager


RECV_MAX = 100000

class ElectrumQuery(object):
    def __init__(self, server, port, ssl=True, tails=True, cache=False):
        self.server = server
        self.port = port
        self.ssl = ssl
        self.tails = tails
        self.cache = cache
        self.dm = DirectoryManager()

    def _create_socket(self):
        s = (socks.create_connection((self.server, self.port),
                                     proxy_type=socks.SOCKS5,
                                     proxy_addr="127.0.0.1",
                                     proxy_port=9050) if self.tails else
             socket.create_connection((self.server, self.port)))
        self.socket = ssl.wrap_socket(s) if self.ssl else s
        print("opened connection to: %s" %
              chill_yellow_str("%s:%d" % (self.server, self.port)))

    def _destroy_socket(self):
        self.socket.close()
        print("closed connection to: %s" %
              chill_yellow_str("%s:%d" % (self.server, self.port)))

    def _query_id_str(self, msg):
        return "%s:%s/%s" % (self.server, self.port, msg)

    def _recv_line(self):
        # electrum terminates response with a newline
        data = b''
        while True:
            packet = self.socket.recv(RECV_MAX)
            #print("packet: %s" % packet)
            data += packet
            if int(packet[-1]) == 10:
                return data

    def query(self, method, params):
        params = [params] if type(params) is not list else params
        msg = json.dumps({"id":      0,
                          "method": method,
                          "params": params}, sort_keys=True)
        qid = self._query_id_str(msg)

        if ".onion" in self.server:
            print("Electrum fetch: %s" % chill_green_str(qid))
        else:
            print("Electrum fetch: %s" % chill_yellow_str(qid))

        if self.cache and self.dm.is_query_cached(qid):
            cache_file = self.dm.get_query_cache_path(qid)
            return FileManager.read_json_info(cache_file)

        self._create_socket()
        self.socket.send(msg.encode() + b'\n')
        msg = self._recv_line()
        response = json.loads(msg.decode())
        self._destroy_socket()
        if 'error' in response.keys():
            sys.exit("*** Error from Electrum server: %s" %
                     json.dumps(response, sort_keys=True))
        if self.cache:
            cache_file = self.dm.get_query_cache_path(qid)
            FileManager.write_text(cache_file, json.dumps(response))
        return response
