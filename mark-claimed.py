#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import sys
import argparse

from lib.claimed_nuggets import ClaimedNuggets

from lib.options import claim_save_file_arg, claim_save_file_arg_validate
from lib.options import nugget_id_arg

###############################################################################
# main
###############################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Mark the output claimed in save file")

    claim_save_file_arg(parser)
    nugget_id_arg(parser)
    settings = parser.parse_args()
    claim_save_file_arg_validate(settings.claim_save_file)

    cn = ClaimedNuggets(settings.claim_save_file)
    if settings.nugget_id not in cn.keys():
        sys.exit("unknown id %s" % settings.nugget_id)
    cn[settings.nugget_id] = True
    cn.write()
