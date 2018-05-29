# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php


import getpass
import sys

from lib.utl.print import print_red, print_chill_green, print_chill_green
from lib.utl.print import chill_green_str

###############################################################################
# tails check
###############################################################################

TAILS_WARNING_1 = """
You are running this script on an OS which is not TAILS, so the required web
requests will go out via normal web channels which can be a leak of privacy.
Server logs of these requests could correlate your Bitcoin addresses to your
current IP address.
"""

TAILS_WARNING_2 = """
If you wish to proceed anyway, use the '--not-tails' option when invoking the
script.
"""

def check_tails(tails_opt):
    if not tails_opt:
        return
    amnesia = getpass.getuser() == "amnesia"
    if amnesia:
        print_chill_green("It appears this script is running on TAILS. Good.")
        return

    print_red(TAILS_WARNING_1)
    print(TAILS_WARNING_2)
    sys.exit("*** not on tails")
