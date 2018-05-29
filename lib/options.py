# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os


ADDRESS_LIST = """list of public Bitcoin addresses for the tool to examine"""

def address_list_arg(parser):
    parser.add_argument('addresses', type=str, nargs="+", help=ADDRESS_LIST)


CLAIM_SAVE_FILE = """Path to file that saves which outputs have been claimed.
Ideally, this should be on an encrypted USB drive e.g.
/media/amnesia/my_drive_name/my_claim_save_file If the file doesn't exist, it
will be created."""

def claim_save_file_arg(parser):
    parser.add_argument('claim_save_file', type=str, help=CLAIM_SAVE_FILE)

def claim_save_file_arg_validate(claim_save_file):
    a = os.path.abspath(claim_save_file)
    d = os.path.dirname(a)
    if not os.path.exists(d):
        os.makedirs(d)

NUGGET_ID = """Unique identifier to output representing some value (nugget)."""

def nugget_id_arg(parser):
    parser.add_argument('nugget_id', type=str, help=NUGGET_ID)


NOT_TAILS = """For using on non-TAILS OSes and opting out of the advanced
privacy protection.  Queries blockchain.info at the normal dns URL rather than
the .onion gateway, send IP request without Tor and generate
bitcoin_fork_claimer commands without proxychains wrapper."""

def not_tails_arg(parser):
    parser.add_argument('--not-tails', action="store_true", help=NOT_TAILS)


CACHE_REQUESTS = """Save copy of successful web requests under /tmp and use the
cached version if available. Avoids repeated redundant queries of the same
information."""

def cache_request_arg(parser):
    parser.add_argument('--cache-requests', action="store_true",
                        help=CACHE_REQUESTS)

BFC_FORCE = """Generate bitcoin_fork_claimer commands with the --force option
to avoid having to type the line for consent."""
def bfc_force_arg(parser):
    parser.add_argument('--bfc-force', action="store_true",
                        help=BFC_FORCE)


COIN_ID = """Selected coin ID for this query."""

def coin_id_arg(parser, ids):
    ids = sorted(list(ids))
    parser.add_argument('coin_id',  action='store', choices=ids, help=COIN_ID)
