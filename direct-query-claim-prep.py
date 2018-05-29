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

from lib.options import address_list_arg, not_tails_arg, cache_request_arg
from lib.options import bfc_force_arg, claim_save_file_arg, coin_id_arg
from lib.options import claim_save_file_arg, claim_save_file_arg_validate

from lib.special_coins import DIRECT_QUERY

###############################################################################
# main
###############################################################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Find balances for a paritcular coin on a list of "
                    "addresses by querying that particular coin's network "
                    "and prepare claiming instructions for a set of provided "
                    "addresses.")

    claim_save_file_arg(parser)
    coin_id_arg(parser, DIRECT_QUERY.keys())
    address_list_arg(parser)
    not_tails_arg(parser)
    cache_request_arg(parser)
    bfc_force_arg(parser)

    settings = parser.parse_args()

    claim_save_file_arg_validate(settings.claim_save_file)
    tails = not settings.not_tails
    check_tails(tails)

    vdb = ValueDb(settings)

    cn = ClaimedNuggets(settings.claim_save_file)
    cn.update_ids(vdb['nuggets'])
    cn.write()
    vdb['nuggets'].mark_claimed(cn)

    DIRECT_QUERY[settings.coin_id](vdb, settings)

    dqr = DirectQueryReport(vdb, settings.coin_id)
    dqr.write()

