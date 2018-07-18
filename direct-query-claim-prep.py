#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import argparse

from lib.value_db import ValueDb
from lib.tails import check_tails

from lib.claimed_nuggets import ClaimedNuggets

from lib.report.direct_query import DirectQueryReport
from lib.special_coins import DIRECT_QUERY

from lib.args import add_args, validate_args



###############################################################################

COIN_ID = """Selected coin ID for this query."""

def coin_id_arg(parser, ids):
    ids = sorted(list(ids))
    parser.add_argument('coin_id',  action='store', choices=ids, help=COIN_ID)

###############################################################################
# main
###############################################################################

ARGS = ['claim_save_file', 'cache_requests', 'address_list', 'not_tails',
        'electrum_server', 'electrum_port', 'electrum_no_ssl', 'bfc_force']

DESCRIPTION = """"Find balances for a paritcular coin on a list of addresses by
querying that particular coin's network and prepare claiming instructions for a
set of provided addresses. Note this sill needs to query the Bitcoin (BTC)
transaction record via block explorer or Electrum server to help understand the
block ranges balances were helds"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    coin_id_arg(parser, DIRECT_QUERY.keys())
    add_args(parser, ARGS)
    settings = parser.parse_args()
    validate_args(settings, ARGS)

    vdb = ValueDb(settings)

    cn = ClaimedNuggets(settings.claim_save_file)
    cn.update_ids(vdb['nuggets'])
    cn.write()
    vdb['nuggets'].mark_claimed(cn)

    DIRECT_QUERY[settings.coin_id](vdb, settings)

    dqr = DirectQueryReport(vdb, settings.coin_id)
    dqr.write()

