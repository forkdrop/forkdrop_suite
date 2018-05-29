# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.address_info import AddressInfo
from lib.nugget_list import NuggetList
from lib.web_data import WebData
from lib.forkdrop_info import ForkdropInfo

###############################################################################
# address set info
###############################################################################

class ValueDb(dict):
    def __init__(self, settings):
        super().__init__()
        addrs = settings.addresses
        addrs.sort()
        self.forkdrop_info = ForkdropInfo()
        self.tails = not settings.not_tails
        self.cache = settings.cache_requests
        self.bfc_force = settings.bfc_force
        self.claim_save_file = settings.claim_save_file
        self.wd = WebData(tails=self.tails, cache=self.cache)

        self['addrs'] = [AddressInfo(self.wd, addr) for addr in addrs]
        self['basic_coins'] = [c for c in self.forkdrop_info['bitcoin'] if
                               self._classify(c) == "basic"]
        self['basic_coins'].sort(key=lambda x: self._coin_sort(x))
        self['tbd_coins'] = [c for c in self.forkdrop_info['bitcoin'] if
                             self._classify(c) == "tbd"]
        self['tbd_coins'].sort(key=lambda x: self._coin_sort(x))
        self['special_coins'] = [c for c in self.forkdrop_info['bitcoin'] if
                                 self._classify(c) == "special"]
        self['special_coins'].sort(key=lambda x: self._coin_sort(x))
        self['registered_coins'] = [c for c in self.forkdrop_info['bitcoin'] if
                                    self._classify(c) == "registered"]
        self['registered_coins'].sort(key=lambda x: self._coin_sort(x))
        self['exchanges'] = self.forkdrop_info['exchanges']
        self['nuggets'] = NuggetList(self, tails=self.tails,
                                     bfc_force=self.bfc_force)

    def _coin_sort(self, coin):
        bfc = (0 if coin['bfc_support'] == "yes" else 1 if
               coin['bfc_support'] == 'special' else 2)
        return "%d %05d" % (bfc, coin['rank'])

    def _classify(self, c):
        if (c['source_chain'] == "Bitcoin Cash (BCH)" and
            c['bfc_support'] == 'no'):
            return 'tbd'
        if c['id'] == "united-bitcoin":
            return 'basic'

        reg_only = c['reg_airdrop'] and not (c['fork'] or c['airdrop'])
        known_block = (c['fork_block'] != "???" and c['fork_block'] != "N/A"
                       and c['fork_block'] != "TBD")
        special = c['bfc_support'] == "special"
        if special:
            return "special"
        elif reg_only:
            return "registered"
        elif known_block:
            return "basic"
        else:
            return "tbd"

    def get_coin_info(self, coin_id):
        coins = [c for c in self.forkdrop_info['bitcoin'] if
                 c['id'] == coin_id]
        assert len(coins) == 1
        return coins[0]
