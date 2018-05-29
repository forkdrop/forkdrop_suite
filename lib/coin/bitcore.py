# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.web_data import WebData

def bitcore_claimer_line(n):
    src_addr = n['src_addr']
    txid = "<%s-airdrop-txid>" % src_addr
    priv_key = "%s-private-key" % n['src_addr']
    dst_addr = "bitcore-destination-address"
    txindex = "<%s-airdrop-txindex>" % src_addr
    satoshis = "<%s-airdrop-satoshis>" % src_addr
    force = "--force " if n.bfc_force else ""
    return ("python2.7 bitcoin_fork_claimer/claimer.py BTX %s %s %s %s"
            " %s--txindex %s --satoshis %s" %
            (txid, priv_key, src_addr, dst_addr, force, txindex, satoshis))

BITCORE_INSTRUCTIONS = """
BitCore has a separate blockchain that aidropped value on BTC addresses as new
transactions. To use the bitcoin_fork_claimer tool privately, the details of
the transactions must be manually found and provided here.

One must use a BitCore node or block explorer to find:

1) The transaction hash (a.k.a transaction ID) which credits the address
2) The transaction index of the specific output
3) The amount of BitCore satoshis credited

This has been automated to access the BitCore block explorer via the
direct-query-claim-prep.py script included in forkdrop_suite. This will gather
the balances and provide a more specific report tailored to claiming Bitcoin
Private.

WARNING: These quereis are less private than blockchain.info queries and may be
less reliable.
"""

UNSPENT_URL = "https://chainz.cryptoid.info/btx/api.dws?q=unspent&active=%s&key=a660e3112b78"

class BitcoreQuery(object):
    def __init__(self, vdb, settings):
        self.vdb = vdb
        self.coin = self.vdb.get_coin_info('bitcore')

        self.addrs = [{'addr':        a,
                       'p2sh_p2wpkh': a[:1] == "3",
                       'bech32':      a[:3] == "bc1"}
                      for a in settings.addresses]

        self.tails = not settings.not_tails
        self.cache = settings.cache_requests

        self.wd = WebData(tails=self.tails, cache=self.cache)
        self._add_nuggets()

    def _add_nuggets(self):
        for a in self.addrs:
            addr = a['addr']
            url = UNSPENT_URL % addr
            unspent_info = self.wd.fetch_web_url_json_info(url)
            for u in unspent_info['unspent_outputs']:
                self.vdb['nuggets'].append_direct_query(a, self.coin,
                                                        u['tx_hash'],
                                                        u['tx_ouput_n'],
                                                        int(u['value']))

BITCORE = {
    'id':           'bitcore',
    'instructions': BITCORE_INSTRUCTIONS,
    'claimer_line': bitcore_claimer_line,
    'direct_query': BitcoreQuery,
}
