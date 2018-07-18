#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import sys
import argparse

from lib.claimed_nuggets import ClaimedNuggets

from lib.options import claim_save_file_arg, claim_save_file_arg_validate
from lib.options import nugget_id_arg

from lib.args import add_args, validate_args

###############################################################################
# main
###############################################################################

ARGS = ['claim_save_file', 'nugget_id']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Mark the output as claimed in save file")

    add_args(parser, ARGS)
    settings = parser.parse_args()
    validate_args(settings, ARGS)

    cn = ClaimedNuggets(settings.claim_save_file)
    if settings.nugget_id not in cn.keys():
        sys.exit("unknown id %s" % settings.nugget_id)
    cn[settings.nugget_id] = True
    cn.write()
