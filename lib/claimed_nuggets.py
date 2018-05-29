# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import json
from lib.utl.print import print_red, print_chill_green
from lib.utl.dir_manager import DirectoryManager
from lib.utl.file_manager import FileManager

###############################################################################
# persisted list of claimed nuggets
###############################################################################

CLAIMED_FILE = "claimed-value-tracking.json"

class ClaimedNuggets(dict):
    def __init__(self, claim_save_file):
        super().__init__()
        self.claimed_file = claim_save_file
        self.read()
        self.dm = DirectoryManager()

    def update_ids(self, nugget_list):
        for n in nugget_list:
            if n['nid'] not in self.keys():
                self[n['nid']] = False

    def write(self):
        l = {nid: claimed for nid, claimed in self.items() if nid != "TBD"}
        FileManager.write_json_info(self.claimed_file, l)
        print_chill_green("\nupdated %s" % self.claimed_file)

    def read(self):
        if not os.path.exists(self.claimed_file):
            return
        l = FileManager.read_json_info(self.claimed_file)
        for nid, claimed in l.items():
            self[nid] = claimed
