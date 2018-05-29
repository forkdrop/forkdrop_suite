# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


import os

from lib.report.base import ReportBase

###############################################################################
# Preamble
###############################################################################

PREAMBLE = """
*** USE THE INFORMATION IN THIS DOCUMENT AT YOUR OWN RISK ***

This is meant to be a guide for using the bitcoin_fork_claimer tool to move
forked coins. It finds and generates parameters for the tool, however it is not
guaranteed to be bug-free. You accept full responsiblity for running this code
and the bitcoin_fork_claimer tool.

*** USE THE INFORMATION IN THIS DOCUMENT AT YOUR OWN RISK ***

This generated document also provides pointers to which exchanges allow
deposits of these coins and some hint as to their KYC requirements. This is not
an endorsement of these exchanges and this information is not guaranteed to be
accurate. Also, some of the non-KYC exchanges may decide to require KYC at
their convenience.

*** USE THE INFORMATION IN THIS DOCUMENT AT YOUR OWN RISK ***

We are not the authors of the bitcoin_fork_claimer tool, and are also not
responsible for any bugs or malicious effect. Please make sure you understand
the code you are running and accept 100% of the risk of anything that happens
as a result.

*** USE THE INFORMATION IN THIS DOCUMENT AT YOUR OWN RISK ***

"""


###############################################################################
# Bitcoin report
###############################################################################


MOVE_BTC_WARNING = """
It is highly recommended that this BTC be moved to different addresses before
these addresses before proceeding to move forked coins. A reasonable method for
doing so is via Electrum which included in TAILS.
"""

MOVED_BTC = """
These addresses do not contain BTC. Excellent.
"""

class BitcoinReport(ReportBase):
    def _unspent_btc(self, addr):
        unspent = 0
        for span in addr['spans'].values():
            if not span['defunded']:
                unspent += span['funded']['value']
        return unspent

    def _gen(self):
        yield ""
        yield "Bitcoin (BTC) detected on provided addresses:"
        yield ""
        warn = False
        for addr in self.vdb['addrs']:
            unspent = self._unspent_btc(addr)
            if unspent != 0:
                yield "%s has %s BTC unspent" % (addr['addr'],
                                                 self._fmt_btc_value(unspent))
                warn = True

        if warn:
            yield MOVE_BTC_WARNING
        else:
            yield MOVED_BTC


###############################################################################
# Private Key Search and Replace
###############################################################################

SEARCH_AND_REPLACE = """
Command invocation parameters for the bitcoin_fork_claimer tool have been
prepared for you in this document. However, strings have been for where your
private keys must be provided in order to actually run the script. Once you
have retrieved your private keys, it is suggested that you use a text editor's
search-and-replace (a.k.a. find-and-replace) functionality to conveniently
insert your private keys.

To keep your private keys secure, it is recommended that they only be accessed
on a secure system and that this document be stored on only an encrypted drive.

We have several guides provied to help with these tasks available at
forkdrop.io:

https://forkdrop.io/secure-live-boot-ubuntu-for-bitcoin-keys
https://forkdrop.io/sd-card-for-saving-files-on-ubuntu-live-boot
https://forkdrop.io/usb-drive-for-saving-files-on-ubuntu-live-boot
https://forkdrop.io/running-bip-39-tool-on-secure-offline-ubuntu-system
https://forkdrop.io/running-bitaddress-tool-on-secure-offline-ubuntu-system

Once you have obtained your private keys, the following strings in this
document are available be replaced throughout with the private key
corresponding to the public bitcoin addresses denoted:
"""

class SearchAndReplaceReport(ReportBase):
    def _gen(self):
        yield SEARCH_AND_REPLACE
        for addr in self.vdb['addrs']:
            yield "%s-private-key" % addr['addr']
        yield ''


###############################################################################
# Proxychains instructions
###############################################################################


CLAIMER_INSTRUCTIONS = """
The bitcoin_fork_claimer tool must be obtained off of GitHub. The lines to
invoke the claimer.py script are assuming that bitcoin_fork_claimer has been
cloned to the same directory as the script which generated this document.
Ideally, this is an encrypted USB drive mounted under /media/amnesia/ on TAILS.

To 'cd' to that directory:

amnesia@amnesia:~$ cd /media/amnesia/mydrive/

To clone the tool off of GitHub:

amnesia@amnesia:/media/amnesia/mydrive/$ git clone https://github.com/ymgve/bitcoin_fork_claimer

Once the cloning is complete, you can 'cd' into this directory and use the 'git
log' command to see what is the top git SHA1 commit id in origin/master:

amnesia@amnesia:/media/amnesia/mydrive/$ cd bitcoin_fork_claimer
amnesia@amnesia:/media/amnesia/mydrive/bitcoin_fork_claimer$ git log

To ensure this code is safe to use, you should check the top SHA1 commit id
against the GitHub web interface to make sure 1) you know the exact version you
are running, 2) you don't see any evidence of tampering with the software and
3) there are no outstanding issues filed that might affect you.
"""

###############################################################################
# Proxychains instructions
###############################################################################


PROXYCHAINS_INSTRUCTIONS = """
In order to move coins with the bitcoin_fork_claimer tool on TAILS, you must us
the localhost proxy provided by the OS in order to connect to the nodes. This
is a required step to make the necessary socket connection for protocol
communication via Tor.

The easiest way to do this is via the Proxychains tool which wraps the
bitcoin_fork_claimer Python process to route traffic through the proxy in a way
that is transparent to the script. However, to use this tool you must manually
install it on TAILS every time the system is booted.

When initially booting up TAILS, in the initial menu that is displayed before
you get to the desktop, you must go into the Advanced settings and set an
administrator password for the session.

To install, from the desktop once you are connected to the network and Tor, you
must open a Terminal application session and run the following two commands:

amnesia@amnesia:~$ sudo apt-get update
amnesia@amnesia:~$ sudo apt-get install proxychains dnsutils

This might take a couple minutes to finish. Select 'Y' when prompted.

Once installed, using the terminal command 'proxychains' in front of a
bitcoin_fork_claimer script invocation will perform the necessary proxy step.

"""


###############################################################################
# Exchanges supporting coin report
###############################################################################

class CoinExchangeReport(ReportBase):
    def __init__(self, vdb, coin, replace_msg=True):
        super().__init__(vdb)
        self.coin = coin
        self.replace_msg = replace_msg

    def _gen(self):
        one = False
        yield "\nnon-KYC exchanges supporting deposits and trade of %s:\n" % (
            self.coin['ticker'])
        for exchange in self.vdb['exchanges']:
            if exchange['kyc_withdraw'] != "False":
                continue
            if self.coin['name'] in set(e['name'] for e in exchange['deposit']):
                one = True
                yield "\t%s" % self._forkdrop_url(exchange['id'])
        if not one:
            yield "\t(none)"
        one = False
        yield "\nKYC exchanges supporting deposits and trade of %s:\n" % (
            self.coin['ticker'])
        for exchange in self.vdb['exchanges']:
            if exchange['kyc_withdraw'] == "False":
                continue
            if self.coin['name'] in set(e['name'] for e in exchange['deposit']):
                one = True
                yield "\t%s" % self._forkdrop_url(exchange['id'])
        if not one:
            yield "\t(none)"
        if not self.replace_msg:
            return
        yield ("\nYou may search-and-replace the string: "
               "%s-destination-address\n"
               "with the address you wish to be the destination for your "
               "%s.") % (self.coin['id'], self.coin['ticker'])



###############################################################################
# Donation Reminder
###############################################################################

DONATION_REMINDER = """
Lots of hard work went into providing this free stack of software.

Support forkdrop.io and the forkdrop_suite tools:

%s

also:

Bitcoin (BTC):               %s
Litecoin (LTC):              %s
%s

~

Support Ymgve's bitcoin_fork_claimer tool via his donation address in his
README.md or seen at: https://github.com/ymgve/bitcoin_fork_claimer

Support the TAILS project at: https://tails.boum.org/donate/

Support the Tor project at:
https://www.torproject.org/donate/donate-options.html.en

Support Tor exit node providers by following suggestions at:
https://blog.torproject.org/support-tor-network-donate-exit-node-providers
"""

OTHERS = "\n(and many other fork coins accepted!)"

class DonationReminder(ReportBase):
    def __init__(self, vdb, coin_id=None):
        super().__init__(vdb)
        self.coin_id = coin_id
    def _coin_lines(self):
        for c in self.vdb.forkdrop_info['bitcoin']:
            if c['donation_addr'] == "":
                continue
            if self.coin_id and c['id'] != self.coin_id:
                continue
            yield "%-28s %s" % ("%s (%s):" % (c['name'], c['ticker']),
                                c['donation_addr'])

    def _gen(self):
        s = "\n".join(self._coin_lines())
        yield DONATION_REMINDER % (s,
                                   self.vdb.forkdrop_info['bitcoin_donation'],
                                   self.vdb.forkdrop_info['litecoin_donation'],
                                   "" if not self.coin_id else OTHERS)


###############################################################################
# Report on claiming a coin from the list of nuggets
###############################################################################

CLAIMED_INSTRUCTIONS = """
Once this value has been moved, this value can be marked as claimed for
subsequent generations of this report by running:

$ %s %s %s
"""

SEGWIT_WARNING = """
This is a segwit (P2WPKH) or P2SH address. This may not work with the
bitcoin_fork_claimer tool and/or the forked coin network may have trouble
crediting balances to this type of output. This is certain to work.
"""

B32_WARNING = """
This is a bech32 address. This may not work with the bitcoin_fork_claimer tool
and/or the forked coin network may have trouble crediting balances to this type
of output. This is not certain to work.
"""

class CoinReport(ReportBase):
    def __init__(self, vdb, coin):
        super().__init__(vdb)
        self.coin = coin
        self.nuggets = [n for n in self.vdb['nuggets'] if
                        n['coin_id'] == self.coin['id'] and n['nid'] != "TBD"]

    def _sort_nuggets(self):
        c_nuggets = [n for n in self.nuggets if n['marked_claimed']]
        u_nuggets = [n for n in self.nuggets if not n['marked_claimed']]
        w_nuggets = [n for n in u_nuggets if (n['segwit_concern'] or
                                              n['b32_concern'])]
        return self.nuggets, c_nuggets, u_nuggets, w_nuggets

    def _summary(self, nuggets, c_nuggets, u_nuggets, w_nuggets):
        for n in c_nuggets:
            yield "%s marked claimed" % n['nid']
        if len(c_nuggets) > 0:
            yield ""

        yield "%s total balances for %s (%s)" % (len(nuggets),
                                                 self.coin['name'],
                                                 self.coin['ticker'])
        yield "%d unclaimed balances for %s (%s)" % (len(u_nuggets),
                                                     self.coin['name'],
                                                     self.coin['ticker'])
        yield ("%d unclaimed balances with segwit/p2sh/b32 concerns for "
               "%s (%s)" % (len(w_nuggets), self.coin['name'],
                            self.coin['ticker']))

    def _addr_warning(self, nugget):
        if not nugget['segwit_concern'] and not nugget['b32_concern']:
            return ""

    def _unclaimed_report(self, u_nuggets):
        yield "bitcoin_fork_claimer script invocations to move this value:"
        for n in u_nuggets:
            yield ""
            yield "-" * 80
            yield "id: %s" % n['nid']
            yield ""
            if n['segwit_concern']:
                yield SEGWIT_WARNING
                yield ""
            if n['b32_concern']:
                yield B32_WARNING
                yield ""
            yield n.claimer_str()
            yield ""
            claim = os.path.join(os.getcwd(), "mark-claimed.py")
            yield CLAIMED_INSTRUCTIONS % (claim, self.vdb.claim_save_file,
                                          n['nid'])
        yield "-" * 80

    def _gen(self):
        nuggets, c_nuggets, u_nuggets, w_nuggets = self._sort_nuggets()

        yield "\n".join(self._summary(nuggets, c_nuggets, u_nuggets,
                                      w_nuggets))

        if len(u_nuggets) == 0:
            yield "\n(nothing to do here)"
            return
        yield str(CoinExchangeReport(self.vdb, self.coin))
        yield "\n".join(self._unclaimed_report(u_nuggets))
