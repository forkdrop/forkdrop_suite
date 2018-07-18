#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import argparse

from lib.web_data import WebData
from lib.utl.dir_manager import DirectoryManager
from lib.utl.file_manager import FileManager

from lib.args import add_args, validate_args


ARGS = ['not_tails']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Pull down the current fork metadata from forkdrop.io")

    add_args(parser, ARGS)
    settings = parser.parse_args()
    validate_args(settings, ARGS)

    wd = WebData(tails=(not settings.not_tails))
    coin_data = wd.fetch_forkdrop_info()
    dm = DirectoryManager()
    p = dm.get_forkdrop_file()
    FileManager.write_json_info(p, coin_data)
