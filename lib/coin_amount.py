# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import sys

from lib.special_coins import COIN_AMOUNT_SPECIAL

###############################################################################
# Coin amount
###############################################################################

SATOSHIS_PER_BTC = 100000000

def coin_amount(satoshis, ratio_a, ratio_c):
    return satoshis * (float(coin['ratio_a']) /
                       float(coin['ratio_c']))

class BasicCoinAmount(object):
    def __init__(self, coin, satoshis):
        self.ratio_a = coin['ratio_a']
        self.ratio_c = coin['ratio_c']
        self.satoshis = satoshis
        self.coin_id = coin['id']

    def _can_calculate(self):
        if self.ratio_a == 0 or self.ratio_c == 0:
            return False
        if not self.satoshis:
            return False
        return True

    def _coin_amount(self):
        return self.satoshis * (float(self.ratio_a) / float(self.ratio_c))

    def amount(self):
        if self.coin_id == 'united-bitcoin':
            return self.satoshis
        if not self._can_calculate():
            sys.exit("something wrong")
            return None
        return self._coin_amount()


class SpecialCoinAmount(object):
    def __init__(self, coin, satoshis):
        self.ratio_a = coin['ratio_a']
        self.ratio_c = coin['ratio_c']
        self.coin_id = coin['id']
        self.satoshis = satoshis

    def _can_calculate(self):
        if self.ratio_a == 0 or self.ratio_c == 0:
            return False
        if not self.satoshis:
            return False
        return True

    def _coin_amount(self):
        return self.satoshis * (float(self.ratio_a) / float(self.ratio_c))

    def amount(self):
        if self.coin_id in COIN_AMOUNT_SPECIAL.keys():
            return COIN_AMOUNT_SPECIAL[self.coin_id](self.satoshis)
        return self._coin_amount()
