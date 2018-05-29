# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.coin.bitcoin_cbc import BITCOIN_CBC
from lib.coin.united_bitcoin import UNITED_BITCOIN
from lib.coin.bitcoin_private import BITCOIN_PRIVATE
from lib.coin.fastbitcoin import FASTBITCOIN
from lib.coin.bitcoin_hush import BITCOIN_HUSH
from lib.coin.bitcore import BITCORE
from lib.coin.bitcoin_candy import BITCOIN_CANDY

coins = [
    BITCOIN_CBC,
    UNITED_BITCOIN,
    BITCOIN_PRIVATE,
    FASTBITCOIN,
    BITCOIN_HUSH,
    BITCORE,
    BITCOIN_CANDY,
]

COIN_QUALIFICATION_SPECIAL = {c['id']: c['qualification'] for c in coins
                              if 'qualification' in c.keys()}


SPECIAL_CLAIMER_LINE = {c['id']: c['claimer_line'] for c in coins
                        if 'claimer_line' in c.keys()}


COIN_AMOUNT_SPECIAL = {c['id']: c['coin_amount'] for c in coins
                       if 'coin_amount' in c.keys()}


SPECIAL_INSTRUCTIONS = {c['id']: c['instructions'] for c in coins
                        if 'instructions' in c.keys()}


DIRECT_QUERY = {c['id']: c['direct_query'] for c in coins
                if 'direct_query' in c.keys()}

