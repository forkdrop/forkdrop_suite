# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import tempfile
from datetime import datetime

from lib.utl.file_manager import FileManager
from lib.utl.dir_manager import DirectoryManager
from lib.utl.print import print_red, print_chill_green, chill_green_str
from lib.utl.print import print_chill_yellow, chill_yellow_str
from lib.special_coins import SPECIAL_INSTRUCTIONS
from lib.report.base import ReportBase

from lib.report.common import PREAMBLE, BitcoinReport, SearchAndReplaceReport
from lib.report.common import CLAIMER_INSTRUCTIONS, PROXYCHAINS_INSTRUCTIONS
from lib.report.common import CoinExchangeReport, CoinReport
from lib.report.common import CLAIMED_INSTRUCTIONS, DonationReminder

###############################################################################
# Per-Coin Breakdown
###############################################################################

PER_COIN_BREAKDOWN = """
coin - name of coin
b - does bitcoin_fork_claimer support this coin? 'S' means it has support, but has special steps
n - number of addresses with balance of coin
nc - number of outputs with balance of coin
uc - number of unclaimed outputs that might be difficult/impossible to claim due to segwit/P2SH/bech32 support concerns
nu - number of outputs with balance of coin that are not marked as claimed
claimed - total balance of coins marked as claimed
concerns - total balance of coins that might be difficult/impossible to claim due to segwit/P2SH/bech32 support concerns
unclaimed - total balance of coin not marked as claimed
"""

class CoinBreakdown(ReportBase):
    def _coin_title(self):
        mt = "b/n/nc/uc/nu"
        return "%-28s %12s %20s %20s %20s" % ("coin", mt, "claimed", "concern",
                                              "unclaimed")
    def _coin_line(self, coin):
        name = "%s (%s)" % (coin['name'], coin['ticker'])
        b = ("T" if coin['bfc_support'] == "yes" else "S" if
                    coin['bfc_support'] == "special" else "F")
        n = self.nuggets.n_addresses_per_coin(coin['id'])
        nc = self.nuggets.n_claimed_outputs_per_coin(coin['id'])
        uc = self.nuggets.n_concern_unclaimed_outputs_per_coin(coin['id'])
        nu = self.nuggets.n_unclaimed_outputs_per_coin(coin['id'])

        s_claimed = self.nuggets.coin_claimed_sum_str(coin['id'])
        s_concern = self.nuggets.coin_concern_unclaimed_sum_str(coin['id'])
        s_unclaimed = self.nuggets.coin_unclaimed_sum_str(coin['id'])

        mt = "%s/%d/%d/%d/%d" % (b, n, nc, uc, nu)
        return "%-28s %12s %20s %20s %20s" % (name, mt, s_claimed, s_concern,
                                              s_unclaimed)


    def _gen(self):
        yield PER_COIN_BREAKDOWN
        yield ("Coins that can be easily moved with bitcoin_fork_claimer "
               "tool:")
        yield self._coin_title()
        yield '-' * 100
        for coin in [c for c in self.vdb['basic_coins'] if
                     c['bfc_support'] == 'yes']:
            yield self._coin_line(coin)

        yield ''
        yield ("Coins that can be moved with bitcoin_fork_claimer "
               "tool using special steps:")
        yield self._coin_title()
        yield '-' * 100
        for coin in self.vdb['special_coins']:
            yield self._coin_line(coin)

        yield ''
        yield "Coins that do not yet have credible tool support for moving:"
        yield self._coin_title()
        yield '-' * 100
        for coin in [c for c in self.vdb['basic_coins'] if
                     c['bfc_support'] == 'no']:
            yield self._coin_line(coin)
        yield ''
        yield 'Coins with unknown/TBD criteria for fork/airdrop:'
        yield '-' * 100
        yield self._coin_title()
        yield '-' * 100
        for coin in self.vdb['tbd_coins']:
            yield self._coin_line(coin)
        yield ''

###############################################################################
# Per-Address Breakdown
###############################################################################

PER_ADDRESS_BREAKDOWN = """
coin - name of coin
b - does bitcoin_fork_claimer support this coin? 'S' means it has support, but has special steps
nc - number of outputs with balance of coin
uc - number of unclaimed outputs that might be difficult/impossible to claim due to segwit/P2SH/bech32 support concerns
nu - number of outputs with balance of coin that are not marked as claimed
claimed - total balance of coins marked as claimed
concerns - total balance of coins that might be difficult/impossible to claim due to segwit/P2SH/bech32 support concerns
unclaimed - total balance of coin not marked as claimed
"""

class AddressBreakdown(ReportBase):
    def _title(self):
        mt = "b/nc/uc/nu"
        return "%-28s %12s %20s %20s %20s" % ("coin", mt, "claimed", "concern",
                                              "unclaimed")

    def _coin_line(self, coin, addr):
        name = "%s (%s)" % (coin['name'], coin['ticker'])
        b = ("T" if coin['bfc_support'] == "yes" else "S" if
                    coin['bfc_support'] == "special" else "F")
        nc = self.nuggets.n_claimed_outputs_per_coin_addr(coin['id'],
                                                          addr['addr'])
        uc = self.nuggets.n_concern_unclaimed_outputs_per_coin_addr(coin['id'],
                                                                   addr['addr'])
        nu = self.nuggets.n_unclaimed_outputs_per_coin_addr(coin['id'],
                                                            addr['addr'])
        s_claimed = self.nuggets.addr_claimed_coin_sum_str(coin['id'],
                                                           addr['addr'])
        s_concern = self.nuggets.addr_concern_unclaimed_coin_sum_str(
            coin['id'], addr['addr'])
        s_unclaimed = self.nuggets.addr_unclaimed_coin_sum_str(coin['id'],
                                                               addr['addr'])
        mt = "%s/%d/%d/%d" % (b, nc, uc, nu)
        return "%-28s %12s %20s %20s %20s" % (name, mt, s_claimed, s_concern,
                                              s_unclaimed)

    def _address_report(self, addr):
        yield "address %s:" % addr['addr']
        yield ""
        yield ("Coins that can be easily moved with bitcoin_fork_claimer "
               "tool:")
        yield self._title()
        yield '-' * 100
        for coin in [c for c in self.vdb['basic_coins'] if
                     c['bfc_support'] == 'yes']:
            yield self._coin_line(coin, addr)

        yield ''
        yield ("Coins that can be moved with bitcoin_fork_claimer "
               "tool using special steps:")
        yield self._title()
        yield '-' * 100
        for coin in self.vdb['special_coins']:
            yield self._coin_line(coin, addr)

        yield ''
        yield "Coins that do not yet have credible tool support for moving:"
        yield self._title()
        yield '-' * 100
        for coin in [c for c in self.vdb['basic_coins'] if
                     c['bfc_support'] == 'no']:
            yield self._coin_line(coin, addr)

        yield ''
        yield 'Coins with unknown/TBD criteria for fork/airdrop:'
        yield '-' * 100
        yield self._title()
        yield '-' * 100
        for coin in self.vdb['tbd_coins']:
            yield self._coin_line(coin, addr)
        yield ""

    def _gen(self):
        yield PER_ADDRESS_BREAKDOWN
        for addr in self.vdb['addrs']:
            yield "\n".join(self._address_report(addr))
        yield ''


###############################################################################
# basic bitcoin_fork_claimer claim instructions
###############################################################################

class BasicClaimReport(ReportBase):
    def _coin_header(self, coin):
        title = "%s (%s):  block %s (%s)" % (coin['name'],
                                             coin['ticker'],
                                             coin['fork_block'],
                                             coin['fork_date'])
        return "\n".join(["=" * 80, title, "=" * 80, ""])

    def _gen(self):
        yield ""
        coins = [c for c in self.vdb['basic_coins'] if
                 c['bfc_support'] == 'yes']
        for coin in coins:
            yield self._coin_header(coin)
            yield str(CoinReport(self.vdb, coin))
            yield ''

###############################################################################
# special bitcoin_fork_claimer claim instructions
###############################################################################

class SpecialCoinReport(CoinReport):
    def _unclaimed_report(self, u_nuggets):
        yield SPECIAL_INSTRUCTIONS[self.coin['id']]
        yield "bitcoin_fork_claimer script invocations to move this value:"
        for n in u_nuggets:
            yield ""
            yield "-" * 80
            yield "id: %s" % n['nid']
            yield ""
            yield n.claimer_str()
            yield ""
            claim = os.path.join(os.getcwd(), "mark-claimed.py")
            yield CLAIMED_INSTRUCTIONS % (claim, self.vdb.claim_save_file,
                                          n['nid'])
        yield "-" * 80


class SpecialClaimReport(BasicClaimReport):
    def _gen(self):
        yield ""
        for coin in self.vdb['special_coins']:
            yield self._coin_header(coin)
            yield str(SpecialCoinReport(self.vdb, coin))
            yield ''

###############################################################################
# Unknown claim report
###############################################################################

UNKNOWN_CLAIMING = """
We are unable to recommend an open-source, peer-reviewed and credible method
for redeeming the value for this coin. There may be methods for claiming it by
running software provided by the project, or via tools which have not been as
thoroughly vetted as the bitcoin_fork_claimer tool. In the future the tools
available are likely to improve.
"""

class UnknownCoinReport(CoinReport):
    def _unclaimed_report(self, u_nuggets):
        yield ""
        for n in u_nuggets:
            yield "-" * 80
            yield "id: %s\n" % n['nid']
            yield "An input of %s holds %s %s" % (
                n['src_addr'], self._fmt_btc(n['coin_amount']),
                self.coin['ticker'])
            yield "from txid %s" % (n['txid'])
        if len(u_nuggets) > 0:
            yield "-" * 80

    def _coin_report(self):
        nuggets, c_nuggets, u_nuggets, w_nuggets = self._sort_nuggets()
        yield "\n".join(self._summary(nuggets, c_nuggets, u_nuggets,
                                      w_nuggets))
        if len(u_nuggets) == 0:
            yield "\n(nothing to do here)"
            return
        yield str(CoinExchangeReport(self.vdb, self.coin, replace_msg=False))
        yield "\n".join(self._unclaimed_report(u_nuggets))


class UnknownClaimReport(BasicClaimReport):
    def _gen(self):
        yield ""
        coins = [c for c in self.vdb['basic_coins'] if
                 c['bfc_support'] == 'no']
        for coin in coins:
            yield self._coin_header(coin)
            yield UNKNOWN_CLAIMING
            yield str(UnknownCoinReport(self.vdb, coin))
            yield ''

###############################################################################
# Unknown value report
###############################################################################

TBD_VALUE = """
The details of this coin are not exactly known and the project and value may
never come to fruition. It is advisable to retain exclusive ownership of your
private keys in order to realize potential future value in this project.
"""

class TbdValueReport(BasicClaimReport):
    def _nugget_report(self, coin):
        nuggets = [n for n in self.vdb['nuggets'] if
                   n['coin_id'] == coin['id']]
        yield ""
        for n in nuggets:
            yield "-" * 80
            yield "%s may hold some amount of %s (%s)" % (
                n['src_addr'], coin['name'], coin['ticker'])
        if len(nuggets) > 0:
            yield "-" * 80

    def _gen(self):
        yield ""
        coins = [c for c in self.vdb['tbd_coins']]
        for coin in coins:
            yield self._coin_header(coin)
            yield TBD_VALUE
            yield "\n".join(self._nugget_report(coin))
            yield ''

###############################################################################
# Itinerary
###############################################################################

REPORT_STR = """
This report contains a breakdown of forked coin value found and instructions
for proceeding to claim. It has been written to a temporary directory. To
preserve a copy, you must manually copy it to an external drive (preferably
encrypted):

amnesia@amnesia:~$ cp %s /media/amnesia/my_drive_name/

The file claimed-value-tracking.json in the current directory can be edited to
track which outputs have been claimed by invoking bitcoin_fork_claimer.
Subsequent re-invocations of the script will count those tracked as 'true' as
having being claimed for the re-generation of the report. The settings in
claimed-value-tracking.json will be preserved through multiple runs of this
script.
"""

class PrepReport(ReportBase):
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
        s.append({"title":   ("Balances Detected on Addresses Broken Down Per "
                              "Coin"),
                  "content": str(AddressBreakdown(self.vdb))})
        s.append({"title":   "Support Good Cypherpunk Tools",
                  "content": str(DonationReminder(self.vdb))})
        s.append({"title":   ("Claming Instructions For Coins With Simple "
                              "bitcoin_fork_claimer Support"),
                  "content": str(BasicClaimReport(self.vdb))})
        s.append({"title":   ("Claming Instructions For Coins With Special "
                              "bitcoin_fork_claimer Support"),
                 "content": str(SpecialClaimReport(self.vdb))})
        s.append({"title":   ("Value Without a Credible Available Method of "
                              "Claiming"),
                  "content": str(UnknownClaimReport(self.vdb))})
        s.append({"title":   ("Indeterminate Value"),
                  "content": str(TbdValueReport(self.vdb))})
        return s

    def write(self):
        dm = DirectoryManager()
        f = dm.get_claim_report_path()
        l = dm.get_claim_report_latest_symlink_path()
        print("")
        FileManager.write_text(f, str(self))
        FileManager.symlink(f, l)
        print(REPORT_STR % f)

