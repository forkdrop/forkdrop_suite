# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

###############################################################################
# print helpers
###############################################################################

RED = '\x1b[1;31;40m'
CHILL_GREEN = '\x1b[0;32;40m'
CHILL_YELLOW = '\x1b[0;33;40m'
ENDC = '\x1b[0m'

def print_red(string):
    print(RED + string + ENDC)

def red_str(string):
    return RED + string + ENDC

def print_chill_green(string):
    print(CHILL_GREEN + string + ENDC)

def chill_green_str(string):
    return CHILL_GREEN + string + ENDC

def print_chill_yellow(string):
    print(CHILL_YELLOW + string + ENDC)

def chill_yellow_str(string):
    return CHILL_YELLOW + string + ENDC
