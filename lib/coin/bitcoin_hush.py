# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.address_convert import ConvertedAddress
from lib.electrum_query import ElectrumQuery

def bitcoin_hush_claimer_line(n):
    src_addr = n['src_addr']
    txid = "<%s-airdrop-txid>" % src_addr
    priv_key = "%s-private-key" % n['src_addr']
    dst_addr = "bitcoin-hush-destination-address"
    txindex = "<%s-airdrop-txindex>" % src_addr
    satoshis = "<%s-airdrop-satoshis>" % src_addr
    force = "--force " if n.bfc_force else ""
    return ("python2.7 bitcoin_fork_claimer/claimer.py BTCH %s %s %s %s"
            " %s--txindex %s --satoshis %s" %
            (txid, priv_key, src_addr, dst_addr, force, txindex, satoshis))

BITCOIN_HUSH_INSTRUCTIONS = """
Bitcoin Hush has a new blockchain that aidropped value on BTC addresses as
new transactions. To use the bitcoin_fork_claimer tool privately, the details
of the transactions mus be manually found and provided here.

One may manually use a Bitcoin Hush node or block explorer to find:

1) The transaction hash (a.k.a transaction ID) which credits the address
2) The transaction index of the specific output
3) The amount of Bitcoin Hush satoshis credited

This has been automated to access the Bitcoin Private network via the
direct-query-claim-prep.py script included in forkdrop_suite. This will gather
the balances and provide a more specific report tailored to claiming Bitcoin
Hush.

WARNING: These quereis are less private than blockchain.info queries and may be
less reliable.

"""


ELECTRUM_SERVER = "electrum1.cipig.net"
ELECTRUM_PORT = 10020

class BitcoinHushQuery(object):
    def __init__(self, vdb, settings):
        self.vdb = vdb
        self.coin = self.vdb.get_coin_info('bitcoin-hush')

        self.addrs = [{'addr':        a,
                       'p2sh_p2wpkh': a[:1] == "3",
                       'bech32':      a[:3] == "bc1"}
                      for a in settings.addresses]

        self.tails = not settings.not_tails
        self.cache = settings.cache_requests
        self.bfc_force = settings.bfc_force

        self._add_nuggets()

    def _add_nuggets(self):
        for a in self.addrs:
            converted_addr = str(ConvertedAddress(a['addr'], "bitcoin-hush"))
            eq = ElectrumQuery(ELECTRUM_SERVER, ELECTRUM_PORT, ssl=False,
                               tails=self.tails, cache=self.cache)
            r = eq.query("blockchain.address.listunspent", converted_addr)
            for r in r['result']:
                self.vdb['nuggets'].append_direct_query(a, self.coin,
                                                        r['tx_hash'],
                                                        r['tx_pos'],
                                                        r['value'])


BITCOIN_HUSH = {
    'id':           'bitcoin-hush',
    'instructions': BITCOIN_HUSH_INSTRUCTIONS,
    'claimer_line': bitcoin_hush_claimer_line,
    'direct_query': BitcoinHushQuery,
}
