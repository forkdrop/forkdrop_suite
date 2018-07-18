# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import sys
import re

from lib.tails import check_tails

from bitcoin.base58 import CBase58Data

###############################################################################

ELECTRUM_SERVER = """Electrum server host to connect to."""

def electrum_server_arg(parser):
    parser.add_argument('-s', '--electrum-server', type=str,
                        help=ELECTRUM_SERVER)

def validate_electrum_server_arg(settings):
    if not settings.electrum_server:
        return
    def is_ip(s):
        return re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                        "\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0"
                        "-5])$", s) is not None
    def is_dns(s):
        return re.match("^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*"
                        "([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$",
                        s) is not None
    if not (is_ip(settings.electrum_server) or
            is_dns(settings.electrum_server)):
        sys.exit("%d is not valid ip or hostname" % settings.electrum_server)

###############################################################################

ELECTRUM_PORT = """Electrum server port to connect to."""

def electrum_port_arg(parser):
    parser.add_argument('-p', '--electrum-port', type=int, default=50002,
                        help=ELECTRUM_PORT)

def validate_electrum_port_arg(settings):
    if not settings.electrum_server:
        return
    assert settings.electrum_port > 0, "tcp port must be positive"
    assert settings.electrum_port <= 65535, "tcp port greater than max"

###############################################################################

ELECTRUM_NO_SSL = """Controles whether the script should connect to electrum
without SSL. Note that SSL is not needed for .onion servers."""

def electrum_no_ssl_arg(parser):
    parser.add_argument('-l', '--electrum-no-ssl',
                        action="store_true", default=False,
                        help=ELECTRUM_NO_SSL)

def validate_electrum_no_ssl_arg(settings):
    pass

###############################################################################

ADDRESS_LIST = """list of public Bitcoin addresses for the tool to examine"""

def address_list_arg(parser):
    parser.add_argument('addresses', type=str, nargs="+", help=ADDRESS_LIST)

def validate_address_list_arg(settings):
    for a in settings.addresses:
        CBase58Data(a)

###############################################################################

CLAIM_SAVE_FILE = """Path to file that saves which outputs have been claimed.
Ideally, this should be on an encrypted USB drive e.g.
/media/amnesia/my_drive_name/my_claim_save_file If the file doesn't exist, it
will be created."""

def claim_save_file_arg(parser):
    parser.add_argument('claim_save_file', type=str, help=CLAIM_SAVE_FILE)

def validate_claim_save_file_arg(settings):
    a = os.path.abspath(settings.claim_save_file)
    d = os.path.dirname(a)
    if not os.path.exists(d):
        os.makedirs(d)

###############################################################################

NUGGET_ID = """Unique identifier to output representing some value (nugget)."""

def nugget_id_arg(parser):
    parser.add_argument('nugget_id', type=str, help=NUGGET_ID)

def validate_nugget_id_arg(settings):
    # TODO
    pass

###############################################################################

NOT_TAILS = """For using on non-TAILS OSes and opting out of the advanced
privacy protection.  Queries blockchain.info at the normal dns URL rather than
the .onion gateway, send IP request without Tor and generate
bitcoin_fork_claimer commands without proxychains wrapper."""

def not_tails_arg(parser):
    parser.add_argument('--not-tails', action="store_true", help=NOT_TAILS)

def validate_not_tails_arg(settings):
    check_tails(not settings.not_tails)

###############################################################################

CACHE_REQUESTS = """Save copy of successful web requests under /tmp and use the
cached version if available. Avoids repeated redundant queries of the same
information."""

def cache_requests_arg(parser):
    parser.add_argument('--cache-requests', action="store_true",
                        help=CACHE_REQUESTS)

def validate_cache_requests_arg(settings):
    pass

###############################################################################

BFC_FORCE = """Generate bitcoin_fork_claimer commands with the --force option
to avoid having to type the line for consent."""

def bfc_force_arg(parser):
    parser.add_argument('--bfc-force', action="store_true",
                        help=BFC_FORCE)

def validate_bfc_force_arg(settings):
    pass

###############################################################################
###############################################################################

ARGS = {
    'electrum_server': {'add':      electrum_server_arg,
                        'validate': validate_electrum_server_arg},
    'electrum_port':   {'add':      electrum_port_arg,
                        'validate': validate_electrum_port_arg},
    'electrum_no_ssl': {'add':      electrum_no_ssl_arg,
                        'validate': validate_electrum_no_ssl_arg},
    'address_list':    {'add':      address_list_arg,
                        'validate': validate_address_list_arg},
    'claim_save_file': {'add':      claim_save_file_arg,
                        'validate': validate_claim_save_file_arg},
    'nugget_id':       {'add':      nugget_id_arg,
                        'validate': validate_nugget_id_arg},
    'not_tails':       {'add':      not_tails_arg,
                        'validate': validate_not_tails_arg},
    'cache_requests':  {'add':      cache_requests_arg,
                        'validate': validate_cache_requests_arg},
    'bfc_force':       {'add':      bfc_force_arg,
                        'validate': validate_bfc_force_arg},
}

def add_args(parser, args):
    for a in args:
        ARGS[a]['add'](parser)

def validate_args(settings, args):
    for a in args:
        ARGS[a]['validate'](settings)
