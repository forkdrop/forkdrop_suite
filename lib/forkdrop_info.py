# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.utl.dir_manager import DirectoryManager
from lib.utl.file_manager import FileManager


class ForkdropInfo(dict):
    def __init__(self):
        super().__init__()
        dm = DirectoryManager()
        f = dm.get_forkdrop_file()
        ff = FileManager.read_json_info(f)
        self.update(ff)
