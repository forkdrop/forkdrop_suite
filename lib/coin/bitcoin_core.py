# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

def bitcoin_core_claimer_line(n):
    src_addr = n['src_addr']
    txid = "<%s-airdrop-txid>" % src_addr
    priv_key = "%s-private-key" % n['src_addr']
    dst_addr = "bitcore-destination-address"
    txindex = "<%s-airdrop-txindex>" % src_addr
    satoshis = "<%s-airdrop-satoshis>" % src_addr
    force = "--force " if n.bfc_force else ""
    return ("python2.7 bitcoin_fork_claimer/claimer.py BTCC %s %s %s %s"
            " %s--txindex %s --satoshis %s" %
            (txid, priv_key, src_addr, dst_addr, force, txindex, satoshis))

BITCOIN_CORE_INSTRUCTIONS = """
Bitcoin Core (BTCC) is a fork of Bitcoin Clashic (BCHC), which forked from
Bitcoin (BTC) on August 1st, 2017. However, Bitcoin Cash (BCH) transactions
have been replayable on Bitcoin Clashic (BCHC), so the balance of Bitcoin Core
(BTCC) on any given address is dependent on a) Bitcoin Cash (BCH) transactions
and b) whether the Bitocin Cash (BCH) transactions have been replayed on the
Bitcoin Clashic (BCHC) chain.

One must use a Bitcoin Core (BTCC) node or block explorer to find:

1) The transaction hash (a.k.a transaction ID) which credits the address
2) The transaction index of the specific output
3) The amount of Bitcoin Core (BTCC) satoshis credited

This process is not yet automated in direct-query-claim-prep.py, but may be in
the future.
"""

BITCOIN_CORE = {
    'id':           'bitcoin-core',
    'instructions':  BITCOIN_CORE_INSTRUCTIONS,
    'claimer_line':  bitcoin_core_claimer_line,
}
