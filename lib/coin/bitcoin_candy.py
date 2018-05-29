# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import json

from lib.address_convert import ConvertedAddress
from lib.web_data import WebData

def bitcoin_candy_claimer_line(n):
    src_addr = n['src_addr']
    txid = "<%s-txid>" % src_addr
    priv_key = "%s-private-key" % n['src_addr']
    dst_addr = "bitcoin-candy-destination-address"
    txindex = "<%s-txindex>" % src_addr
    satoshis = "<%s-satoshis>" % src_addr
    force = "--force " if n.bfc_force else ""
    return ("python2.7 bitcoin_fork_claimer/claimer.py CDY %s %s %s %s"
            " %s--txindex %s --satoshis %s" %
            (txid, priv_key, src_addr, dst_addr, force, txindex, satoshis))

BITCOIN_CANDY_INSTRUCTIONS = """
Bitcoin Candy (CDY) is forked from the Bitcoin Cash (BCH) blockchain at block
512666 on 2018-01-12. BCH transactions between it's creation on 2017-08-01 and
this fork block are relevant for credited CDY balances. Querying
blockchain.info here can only show balances that came from unmoved BTC.

One must use a Bitcoin Candy node or block explorer to find:

1) The transaction hash (a.k.a transaction ID) which credits the address
2) The transaction index of the specific output
3) The amount of Bitcoin Candy satoshis credited

This has been automated to access the Bitcoin Candy block explorer via the
direct-query-claim-prep.py script included in forkdrop_suite. This will gather
the balances and provide a more specific report tailored to claiming Bitcoin
Candy.

WARNING: These queries are less private than blockchain.info queries and may be
less reliable.

"""

class BitcoinCandyQuery(object):
    def __init__(self, vdb, settings):
        self.vdb = vdb
        self.coin = self.vdb.get_coin_info('bitcoin-candy')

        self.addrs = [{'addr':        a,
                       'p2sh_p2wpkh': a[:1] == "3",
                       'bech32':      a[:3] == "bc1"}
                      for a in settings.addresses]

        self.tails = not settings.not_tails
        self.cache = settings.cache_requests

        self.wd = WebData(tails=self.tails, cache=self.cache)
        self.explorer = self.coin['explorer'].strip('/')

        self._add_nuggets()

    def _add_nuggets(self):
        for a in self.addrs:
            converted_addr = str(ConvertedAddress(a['addr'], "bitcoin-candy"))
            aapi = "%s/insight-api/addr/%s" % (self.explorer, converted_addr)
            addr_info = self.wd.fetch_web_url_json_info(aapi)
            for t in addr_info['transactions']:
                tapi = "%s/insight-api/tx/%s" % (self.explorer, t)
                tx_info = self.wd.fetch_web_url_json_info(tapi)
                for o in tx_info['vout']:
                    if o['scriptPubKey']['addresses'][0] != converted_addr:
                        continue
                    n = o['n']
                    satoshis = int(float(o['value']) * 100000)
                    self.vdb['nuggets'].append_direct_query(a, self.coin,
                                                            t, o['n'],
                                                            satoshis)

BITCOIN_CANDY = {
    'id':           'bitcoin-candy',
    'instructions': BITCOIN_CANDY_INSTRUCTIONS,
    'claimer_line': bitcoin_candy_claimer_line,
    'direct_query': BitcoinCandyQuery,
}
