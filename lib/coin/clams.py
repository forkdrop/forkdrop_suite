# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

def clams_coin_amount(satoshis):
    # airdrops 4.60545574 to addresses > 0.0001 BTC
    return 460545574 if satoshis > 10000 else 0

CLAMS = {
    'id':           'clams',
    'coin_amount':  clams_coin_amount,
}
