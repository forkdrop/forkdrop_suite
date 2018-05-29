# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

def united_bitcoin_qualification(span):
    ubtc_start = 494000
    ubtc_end = 502315
    if not span['defunded']:
        return None
    if (span['defunded']['block'] < ubtc_end and
        span['defunded']['block'] > ubtc_start):
        return span['defunded']['value']
    return None

UNITED_BITCOIN = {
    'id':            'united-bitcoin',
    'qualification': united_bitcoin_qualification,
}
