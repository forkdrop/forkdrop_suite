# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


import sys

from lib.coin_amount import BasicCoinAmount, SpecialCoinAmount
from lib.special_coins import SPECIAL_CLAIMER_LINE, COIN_AMOUNT_SPECIAL

###############################################################################
# Nuggets - A nugget is a piece of value that most often corresponds to an
# unspent output on a fork chain.
###############################################################################

class Nugget(dict):
    def __init__(self, addr, coin, tails=True, bfc_force=True):
        super().__init__()
        self['ticker'] = coin['ticker']
        self['coin_id'] = coin['id']
        self['src_addr'] = addr['addr']
        self['marked_claimed'] = False

        segwit_concern = coin['segwit'] == "False" or coin['segwit'] == "???"
        self['segwit_concern'] = segwit_concern and (addr['p2sh_p2wpkh'] or
                                                     addr['bech32'])

        b32_concern = coin['bech32'] == "False" or coin['bech32'] == "???"
        self['b32_concern'] = b32_concern and addr['bech32']

        self.proxychains = tails
        self.bfc_force = bfc_force


class BasicNugget(Nugget):
    def __init__(self, addr, coin, span, tails=True, bfc_force=True):
        super().__init__(addr, coin, tails=tails, bfc_force=bfc_force)

        self['satoshis'] = span['funded']['value']
        self['txindex'] = span['funded']['n']
        self['txid'] = span['funded']['hash']
        self['nid'] = self._nugget_id()
        self['coin_amount'] = (SpecialCoinAmount(coin, self['satoshis']).amount() if
                               self['coin_id'] in COIN_AMOUNT_SPECIAL.keys() else
                               BasicCoinAmount(coin, self['satoshis']).amount())
        self['type'] = "basic"


    def _nugget_id(self):
        return "%s-%s-%s-%s" % (self['coin_id'],
                                self['src_addr'][:15],
                                self['satoshis'],
                                self['txid'][:15])

    def claimer_str(self):
        assert self['satoshis']
        ticker = self['ticker']
        txid = self['txid']
        src_addr = self['src_addr']
        priv_key = "%s-private-key" % self['src_addr']
        dst_addr = "%s-destination-address" % self['coin_id']
        txindex = self['txindex']
        satoshis = self['satoshis']
        proxy = "proxychains " if self.proxychains else ""
        force = "--force " if self.bfc_force else ""
        return (("%spython2.7 bitcoin_fork_claimer/claimer.py %s %s "
                 "%s %s %s %s--txindex %d --satoshis %d") %
                (proxy, ticker, txid, priv_key, src_addr, dst_addr, force,
                 txindex, satoshis))


class SpecialNugget(Nugget):
    def __init__(self, addr, coin, satoshis, tails=True, bfc_force=True):
        super().__init__(addr, coin, tails=tails, bfc_force=bfc_force)
        self.spans = addr['spans'].values()
        self['nid'] = "%s-%s" % (coin['id'], addr['addr'][:15])
        self['coin_amount'] = SpecialCoinAmount(coin, satoshis).amount()
        self['type'] = "special"

    def claimer_str(self):
        if self['coin_id'] not in SPECIAL_CLAIMER_LINE.keys():
            sys.exit("unknown claimer line for %s" % self['coin_id'])
        line = SPECIAL_CLAIMER_LINE[self['coin_id']](self)
        return "proxychains %s" % line if self.proxychains else line


class TbdNugget(Nugget):
    def __init__(self, addr, coin, tails=True, bfc_force=True):
        super().__init__(addr, coin, tails=tails, bfc_force=bfc_force)
        self['coin_amount'] = None
        self['nid'] = "%s-%s" % (coin['id'], addr['addr'][:15])
        self['type'] = "tbd"

    def claimer_str(self):
        sys.exit("asked for claimer str on TbdNugget?")


class DirectQueryNugget(Nugget):
    def __init__(self, addr, coin, txid, txindex, satoshis, tails=True,
                 bfc_force=True, fbtc=False):
        super().__init__(addr, coin, tails=tails, bfc_force=bfc_force)
        self.fbtc = fbtc
        self['satoshis'] = satoshis
        self['txindex'] = txindex
        self['txid'] = txid
        self['nid'] = self._nugget_id()
        self['coin_amount'] = SpecialCoinAmount(coin, satoshis).amount()
        self['type'] = "direct_query"


    def _nugget_id(self):
        if self.fbtc:
            return "%s-%s-%s" % (self['coin_id'],
                                 self['src_addr'][:15],
                                 self['satoshis'])
        return "%s-%s-%s-%s" % (self['coin_id'],
                                self['src_addr'][:15],
                                self['satoshis'],
                                self['txid'][:15])

    def claimer_str(self):
        assert self['satoshis']
        proxy = "proxychains " if self.proxychains else ""
        priv_key = "%s-private-key" % self['src_addr']
        src_addr = self['src_addr']
        dst_addr = "%s-destination-address" % self['coin_id']
        satoshis = self['satoshis']
        if self.fbtc:
            return ("%spython2.7 bitcoin_fork_claimer/fbtcclaimer.py %s %s %s "
                    "%s") % (proxy, priv_key, src_addr, dst_addr, satoshis)

        ticker = self['ticker']
        txid = self['txid']
        force = "--force " if self.bfc_force else ""
        txindex = self['txindex']
        return (("%spython2.7 bitcoin_fork_claimer/claimer.py %s %s "
                 "%s %s %s %s--txindex %d --satoshis %d") %
                (proxy, ticker, txid, priv_key, src_addr, dst_addr, force,
                 txindex, satoshis))
