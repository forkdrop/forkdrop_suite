#!/usr/bin/env python3
# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import argparse

from lib.tails import check_tails
from lib.options import not_tails_arg

from lib.web_data import WebData
from lib.utl.dir_manager import DirectoryManager
from lib.utl.file_manager import FileManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Pull down the current fork metadata from forkdrop.io")
    not_tails_arg(parser)
    settings = parser.parse_args()

    tails = not settings.not_tails
    check_tails(tails)

    wd = WebData(tails=tails)
    coin_data = wd.fetch_forkdrop_info()
    dm = DirectoryManager()
    p = dm.get_forkdrop_file()
    FileManager.write_json_info(p, coin_data)
