#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import argparse


from lib.address_convert import ConvertReport


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert public Bitcoin addresses to public addresses of "
                    "other coins.")

    parser.add_argument('addresses', type=str, nargs="+",
                        help="list of public bitcoin addresses to convert")

    settings = parser.parse_args()

    print("")
    for addr in settings.addresses:
        print("input: %s:" % addr)
        print("")
        print(str(ConvertReport(addr)))
        print("")
