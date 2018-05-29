# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.utl.constants import SATOSHIS_PER_BTC

def fastbitcoin_claimer_line(n):
    src_addr = n['src_addr']
    priv_key = "%s-private-key" % n['src_addr']
    dst_addr = "fastbitcoin-destination-address"
    satoshis = "<%s-airdrop-satoshis>" % src_addr
    return ("python2.7 bitcoin_fork_claimer/fbtcclaimer.py %s %s %s %s" %
            (priv_key, src_addr, dst_addr, satoshis))

FASTBITCOIN_INSTRUCTIONS = """
WARNING - this claiming solution is far from ideal. Fastbitcoin doesn't have a
functional block explorer and is significantly different from bitcoin. If this
seems sketchy, this is because *it* *is* *sketchy*.

FastBitcoin is a new blockchain with a different codebase (derived from PIVX)
that airdropped value on BTC addresses. By the nature of this blockchain, there
are not txids and txindex like there are with Bitcoin. These do not have to be
provided.

What we have to do is guess about the amounts that you have beeen credited in
fastbittcoin from the blockchain.info queries and the rules of the airdrop.
bitcoin_fork_claimer will take this amount and blindly create this transaction
for this amount minus the transaction fee. If the given amount was too large,
the transaction will be rejected by the network. If the given amount is too
small, the remainder will go to the miner as a transaction fee.

One way to be more certain may be to run a Fastbitcoin node, but that might
come with other tradeoffs.
"""


class FastbitcoinQuery(object):
    def __init__(self, vdb, settings):
        self.vdb = vdb
        self.coin = self.vdb.get_coin_info('fastbitcoin')

        self.addrs = [{'addr':        a,
                       'p2sh_p2wpkh': a[:1] == "3",
                       'bech32':      a[:3] == "bc1"}
                      for a in settings.addresses]

        self.tails = not settings.not_tails
        self.bfc_force = settings.bfc_force
        self.nuggets = self.vdb['nuggets']
        self._add_nuggets()

    def _add_nuggets(self):
        for a in self.addrs:
            s_unclaimed = self.nuggets.addr_unclaimed_coin_sum_str(
                self.coin['id'], a['addr'])
            satoshis = int(float(s_unclaimed) * SATOSHIS_PER_BTC)
            self.nuggets.append_direct_query(a, self.coin, "", "", satoshis,
                                             fbtc=True)

FASTBITCOIN = {
    'id':           'fastbitcoin',
    'instructions': FASTBITCOIN_INSTRUCTIONS,
    'claimer_line': fastbitcoin_claimer_line,
    'direct_query': FastbitcoinQuery,
}
