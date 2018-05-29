# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import json

from lib.utl.print import print_chill_green
from lib.utl.dir_manager import DirectoryManager

class FileManager(object):
    def write_text(path, content):
        file = open(path, 'w')
        file.write(content)
        file.close()
        print_chill_green("wrote: %s" % path)

    def write_json_info(path, d):
        FileManager.write_text(path, json.dumps(d, indent=1, sort_keys=True))

    def read_text(path):
        file = open(path, 'r')
        content = file.read()
        file.close()
        print_chill_green("read: %s" % path)
        return content

    def read_json_info(path):
        return json.loads(FileManager.read_text(path))


    def symlink(tgt_path, sym_path):
        dm = DirectoryManager()

        os.symlink(tgt_path, dm.get_tmp_symlink_path())
        os.rename(dm.get_tmp_symlink_path(), sym_path)
        print_chill_green("symlinked %s" % sym_path)
