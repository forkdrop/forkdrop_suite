# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import hashlib
import tempfile
from datetime import datetime

FORKDROP_FILE = "forkdrop-data.json"

class DirectoryManager(object):
    def __init__(self):
        self.tmp_dir = os.path.join(tempfile.gettempdir(), "forkdrop_suite")
        self._make_dirs_exist(self.tmp_dir)
        if not os.path.exists(".git/"):
            sys.exit("Must be executed from base of the forkdrop_suite "
                     "repository clone.")
        self.cwd = os.getcwd()
        self.forkdrop_file = os.path.join(self.cwd, FORKDROP_FILE)

    def _make_dirs_exist(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def get_query_cache_path(self, query_str):
        filename = hashlib.md5(query_str.encode()).hexdigest() + ".cached"
        return os.path.join(self.tmp_dir, filename)

    def is_query_cached(self, query_str):
        return os.path.exists(self.get_query_cache_path(query_str))

    def get_forkdrop_file(self):
        return self.forkdrop_file

    def get_claim_report_path(self):
        time_str = datetime.now().isoformat("-")
        filename = "claim-report-generated-%s.txt" % time_str
        return os.path.join(self.tmp_dir, filename)

    def get_claim_report_latest_symlink_path(self):
        return os.path.join(self.tmp_dir, "claim-report-latest.txt")

    def get_tmp_symlink_path(self):
        return os.path.join(self.tmp_dir, "tmplink.txt")

    def get_direct_query_report_path(self, coin_id):
        time_str = datetime.now().isoformat("-")
        filename = "%s-direct-query-report-generated-%s.txt" % (coin_id,
                                                                time_str)
        return os.path.join(self.tmp_dir, filename)

    def get_direct_query_report_latest_symlink_path(self, coin_id):
        return os.path.join(self.tmp_dir,
                            "%s-direct-query-report-latest.txt" % coin_id)
