# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.claimed_nuggets import ClaimedNuggets
from lib.nugget import BasicNugget, SpecialNugget, TbdNugget, DirectQueryNugget

from lib.special_coins import COIN_QUALIFICATION_SPECIAL

###############################################################################
# Amount of satoshis that qualify for airdrops of the 'special' category
###############################################################################

class SpecialSatoshis(object):
    def __init__(self, coin, spans):
        self.spans = spans
        self.coin = coin

    def _span_satoshis(self):
        if self.coin['id'] in COIN_QUALIFICATION_SPECIAL:
            qualifies = COIN_QUALIFICATION_SPECIAL[self.coin['id']]
            for span in self.spans:
                satoshis = qualifies(span)
                if satoshis != None:
                    yield satoshis
        else:
            for span in self.spans:
                block = int(self.coin['fork_block'])
                if span['defunded']:
                    if (span['funded']['block'] < block and
                        span['defunded']['block'] >= block):
                        yield span['funded']['value']
                else:
                    if span['funded']['block'] < block:
                        yield span['funded']['value']

    def calc_satoshis(self):
        s_list = list(self._span_satoshis())
        if len(s_list) == 0:
            return 0
        return sum(s_list)

###############################################################################
# All nuggets that are found from the address info
###############################################################################

SATOSHIS_PER_BTC = 100000000

def fmt_btc(satoshis):
    return "%0.8f" % (satoshis / float(SATOSHIS_PER_BTC))

class NuggetList(list):
    def __init__(self, vdb, tails=True, bfc_force=False):
        self.vdb = vdb
        self.tails = tails
        self.bfc_force = bfc_force
        self._gen_list()

    def mark_claimed(self, claimed):
        for n in self:
            if n['nid'] in claimed.keys():
                n['marked_claimed'] = claimed[n['nid']]
            else:
                n['marked_claimed'] = False

    def append_direct_query(self, addr, coin, txid, txindex, satoshis,
                            fbtc=False):
        n = DirectQueryNugget(addr, coin, txid, txindex, satoshis, self.tails,
                              self.bfc_force, fbtc=fbtc)
        self.append(n)

    def _spans_coin(self, coin_block, span):
        if span['defunded']:
            return (span['funded']['block'] < coin_block and
                    span['defunded']['block'] >= coin_block)
        else:
            return span['funded']['block'] < coin_block

    def _gen_basic_list(self, addr):
        for coin in self.vdb['basic_coins']:
            if coin['id'] == "united-bitcoin":
                # UBTC is weird - fudge for noew
                for span in addr['spans'].values():
                    ss = SpecialSatoshis(coin, [span])
                    s = ss.calc_satoshis()
                    if s != 0:
                        self.append(BasicNugget(addr, coin, span,
                                                tails=self.tails,
                                                bfc_force=self.bfc_force))
            else:
                for span in addr['spans'].values():
                    if self._spans_coin(int(coin['fork_block']), span):
                        self.append(BasicNugget(addr, coin, span,
                                                tails=self.tails,
                                                bfc_force=self.bfc_force))


    def _get_special_list(self, addr):
        for coin in self.vdb['special_coins']:
            ss = SpecialSatoshis(coin, addr['spans'].values())
            s = ss.calc_satoshis()
            if s != 0:
                self.append(SpecialNugget(addr, coin, s, tails=self.tails,
                                          bfc_force=self.bfc_force))

    def _get_tbd_list(self, addr):
        for coin in self.vdb['tbd_coins']:
            self.append(TbdNugget(addr, coin, tails=self.tails,
                                  bfc_force=self.bfc_force))

    def _gen_list(self):
        for addr in self.vdb['addrs']:
            # basic nuggets - spans the fork block
            self._gen_basic_list(addr)
            # special nuggets - different coin value critera
            self._get_special_list(addr)
            # tbd nuggets - address had BTC value somehow, someway, but
            # we don't know the full critera of these coins yet.
            self._get_tbd_list(addr)

    def _iter_nuggets(self):
        for n in self:
            yield n

    def _iter_nuggets_addr(self, addr):
        for n in self._iter_nuggets():
            if n['src_addr'] == addr:
                yield n

    def _iter_nuggets_coin(self, coin_id):
        for n in self._iter_nuggets():
            if n['coin_id'] == coin_id:
                yield n

    def _iter_nuggets_addr_coin(self, addr, coin_id):
        for n in self._iter_nuggets_coin(coin_id):
            if n['src_addr'] == addr:
                yield n

    def _unclaimed(self, nuggets):
        for n in nuggets:
            if not n['marked_claimed']:
                yield n

    def _claimed(self, nuggets):
        for n in nuggets:
            if n['marked_claimed']:
                yield n

    def _concern(self, nuggets):
        for n in nuggets:
            if n['segwit_concern'] or n['b32_concern']:
                yield n

    def coin_sum_str(self, coin_id):
        coin_nuggets = [n['coin_amount'] for n in
                        self._iter_nuggets_coin(coin_id)]
        unknown = None in coin_nuggets
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(coin_nuggets))

    def coin_unclaimed_sum_str(self, coin_id):
        unclaimed = self._unclaimed(self._iter_nuggets_coin(coin_id))
        coin_nuggets = [n['coin_amount'] for n in unclaimed]

        unknown = None in coin_nuggets
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(coin_nuggets))

    def coin_concern_unclaimed_sum_str(self, coin_id):
        unclaimed = self._unclaimed(self._iter_nuggets_coin(coin_id))
        concern = self._concern(unclaimed)
        coin_nuggets = [n['coin_amount'] for n in concern]

        unknown = None in coin_nuggets
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(coin_nuggets))

    def coin_claimed_sum_str(self, coin_id):
        claimed = self._claimed(self._iter_nuggets_coin(coin_id))
        coin_nuggets = [n['coin_amount'] for n in claimed]
        unknown = None in coin_nuggets
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(coin_nuggets))

    def n_addresses_per_coin(self, coin_id):
        return len(set(n['src_addr'] for n in
                       self._iter_nuggets_coin(coin_id)))

    def n_outputs_per_coin(self, coin_id):
        return len(set(n['nid'] for n in self._iter_nuggets_coin(coin_id)))

    def n_unclaimed_outputs_per_coin(self, coin_id):
        return len(set(n['nid'] for n in
                       self._unclaimed(self._iter_nuggets_coin(coin_id))))

    def n_concern_unclaimed_outputs_per_coin(self, coin_id):
        return len(set(n['nid'] for n in
                       self._concern(self._unclaimed(
                                            self._iter_nuggets_coin(coin_id)))))

    def n_warn_unclaimedclaimed_outputs_per_coin(self, coin_id):
        return len(set(n['nid'] for n in
                       self._claimed(self._iter_nuggets_coin(coin_id))))

    def n_claimed_outputs_per_coin(self, coin_id):
        return len(set(n['nid'] for n in
                       self._claimed(self._iter_nuggets_coin(coin_id))))

    def addr_coin_sum_str(self, coin_id, addr):
        nuggets = self._iter_nuggets_addr_coin(addr, coin_id)
        amounts = [n['coin_amount'] for n in nuggets]
        unknown = None in amounts
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(amounts))

    def addr_unclaimed_coin_sum_str(self, coin_id, addr):
        nuggets = self._unclaimed(self._iter_nuggets_addr_coin(addr, coin_id))
        amounts = [n['coin_amount'] for n in nuggets]
        unknown = None in amounts
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(amounts))

    def addr_concern_unclaimed_coin_sum_str(self, coin_id, addr):
        unclaimed = self._unclaimed(self._iter_nuggets_addr_coin(addr, coin_id))
        nuggets = self._concern(unclaimed)
        amounts = [n['coin_amount'] for n in nuggets]
        unknown = None in amounts
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(amounts))

    def addr_claimed_coin_sum_str(self, coin_id, addr):
        nuggets = self._claimed(self._iter_nuggets_addr_coin(addr, coin_id))
        amounts = [n['coin_amount'] for n in nuggets]
        unknown = None in amounts
        if unknown:
            return "(TBD value)"
        return fmt_btc(sum(amounts))

    def n_outputs_per_coin_addr(self, coin_id, addr):
        nuggets = self._iter_nuggets_addr_coin(addr, coin_id)
        return len(set(n['nid'] for n in nuggets))

    def n_unclaimed_outputs_per_coin_addr(self, coin_id, addr):
        nuggets = self._unclaimed(self._iter_nuggets_addr_coin(addr, coin_id))
        return len(set(n['nid'] for n in nuggets))

    def n_concern_unclaimed_outputs_per_coin_addr(self, coin_id, addr):
        unclaimed = self._unclaimed(self._iter_nuggets_addr_coin(addr, coin_id))
        nuggets = self._concern(unclaimed)
        return len(set(n['nid'] for n in nuggets))

    def n_claimed_outputs_per_coin_addr(self, coin_id, addr):
        nuggets = self._claimed(self._iter_nuggets_addr_coin(addr, coin_id))
        return len(set(n['nid'] for n in nuggets))

    def __str__(self):
        return "\n".join(n._nugget_id() for n in self)
