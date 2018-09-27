#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import argparse

from lib.value_db import ValueDb
from lib.claimed_nuggets import ClaimedNuggets
from lib.report.prep import PrepReport
from lib.tails import check_tails

from lib.options import address_list_arg, not_tails_arg, cache_request_arg
from lib.options import bfc_force_arg
from lib.options import claim_save_file_arg, claim_save_file_arg_validate

from lib.args import add_args, validate_args

###############################################################################
# main
###############################################################################

ARGS = ['claim_save_file', 'electrum_server', 'electrum_port',
        'electrum_no_ssl', 'cache_requests', 'address_list', 'not_tails',
        'bfc_force']

DESCRIPTION = """Find fork/airdrop balances and prepare claiming instructions
for a set of provided addresses. Defaults to pulling transaction info from
blockchain.info via their .onion access point (or via their web url if running
with --not-tails).  Otherwise, it is reccomended to use the ELECTRUM_SERVER
option to gather info from an electrum server of your choosing.)
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    add_args(parser, ARGS)
    settings = parser.parse_args()
    validate_args(settings, ARGS)

    vdb = ValueDb(settings)

    cn = ClaimedNuggets(settings.claim_save_file)
    cn.update_ids(vdb['nuggets'])
    cn.write()

    vdb['nuggets'].mark_claimed(cn)

    i = PrepReport(vdb)
    i.write()
