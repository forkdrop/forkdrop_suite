# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import tempfile
from datetime import datetime

from lib.utl.file_manager import FileManager
from lib.utl.dir_manager import DirectoryManager
from lib.utl.print import print_red, print_chill_green, chill_green_str

from lib.report.base import ReportBase
from lib.report.common import PREAMBLE, BitcoinReport, SearchAndReplaceReport
from lib.report.common import CLAIMER_INSTRUCTIONS, PROXYCHAINS_INSTRUCTIONS
from lib.report.common import DonationReminder
from lib.report.common import CoinExchangeReport, CoinReport


###############################################################################
# coin claim report
###############################################################################

class DirectQueryCoinReport(CoinReport):
    def __init__(self, vdb, coin):
        self.coin = coin

        super().__init__(vdb, self.coin)
        self.nuggets = [n for n in self.vdb['nuggets'] if
                        (n['coin_id'] == self.coin['id'] and
                         n['type'] == "direct_query")]

###############################################################################
# value summary
###############################################################################

VALUE_SUMMARY = """
According to blockchain.info and what we know about this coin, the credited
value of this type on these addresses is below. However, if value has
ben subsequently sent, the direct query will find it in addition to what
is listed here:
"""


class DirectQueryValueSummary(ReportBase):
    def __init__(self, vdb, coin):
        self.coin_id = coin['id']
        super().__init__(vdb)
        self.nuggets = [n for n in self.vdb['nuggets'] if
                        (n['coin_id'] == self.coin_id and
                         n['type'] != "direct_query")]

    def _gen(self):
        yield ""
        yield VALUE_SUMMARY
        yield ""
        unclaimed = [n for n in self.nuggets if not n['marked_claimed']]
        for n in unclaimed:
            yield "%s has %s %s unclaimed" % (
                n['src_addr'], self._fmt_btc(n['coin_amount']), n['ticker'])

        yield ""
        total = self._fmt_btc(sum(n['coin_amount'] for n in unclaimed))
        yield "%s total credited and not marked as claimed" % (total)

###############################################################################
# Generate report
###############################################################################

REPORT_STR = """
This report contains a breakdown of %s value found and
instructions for proceeding to claim. It has been written to a temporary
directory. To preserve a copy, you must manually copy it to an external drive
(preferably encrypted):

amnesia@amnesia:~$ cp %s /media/amnesia/my_drive_name/

The file claimed-value-tracking.json in the current directory can be edited to
track which outputs have been claimed by invoking bitcoin_fork_claimer.
Subsequent re-invocations of the script will count those tracked as 'true' as
having being claimed for the re-generation of the report. The settings in
claimed-value-tracking.json will be preserved through multiple runs of this
script.
"""

class DirectQueryReport(ReportBase):
    def __init__(self, vdb, coin_id):
        super().__init__(vdb)
        self.coin_id = coin_id
        self.coin = vdb.get_coin_info(coin_id)
        self.name = "%s (%s)" % (self.coin['name'], self.coin['ticker'])

    def _sections(self):
        s = []
        s.append({"title":  "Premable",
                  "content": PREAMBLE})
        s.append({"title":   "Table of Contents",
                  "content": None}) # will generate TOC content
        s.append({"title":   "Warning to Move BTC",
                  "content": str(BitcoinReport(self.vdb))})
        s.append({"title":   "Obtaining the bitcoin_fork_claimer Tool on TAILS",
                  "content": CLAIMER_INSTRUCTIONS})
        if self.vdb.tails:
            s.append({"title":   "Preparing Proxychains Tool on TAILS",
                      "content": PROXYCHAINS_INSTRUCTIONS})
        s.append({"title":   "Private Key Search-and-replace Instructions",
                  "content": str(SearchAndReplaceReport(self.vdb))})
        s.append({"title":   "%s Value Summary" % self.name,
                  "content": str(DirectQueryValueSummary(self.vdb, self.coin))})
        s.append({"title":   "Support Good Cypherpunk Tools",
                  "content": str(DonationReminder(self.vdb,
                                                  coin_id=self.coin_id))})
        s.append({"title":   "Claming Instructions for %s" % self.name,
                  "content": str(DirectQueryCoinReport(self.vdb, self.coin))})
        return s

    def write(self):
        dm = DirectoryManager()
        f = dm.get_direct_query_report_path(self.coin['id'])
        l = dm.get_direct_query_report_latest_symlink_path(self.coin['id'])
        print("")
        FileManager.write_text(f, str(self))
        FileManager.symlink(f, l)
        print(REPORT_STR % (self.name, f))
