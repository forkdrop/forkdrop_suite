
Forkdrop Suite
==============

A collection of tools and utilities to assist with privately and securely claiming of Bitcoin fork tokens. It is designed to be maximally secure and private by default by running on [TAILS](https://tails.boum.org) and only issuing external queries via Tor. It utilizes [blockchain.info's onion gateway](https://blockchainbdgpzk.onion) for obtaining Bitcoin balance info for specific addresses.

The tools included find (infer) fork and airdrop coins from a list of public addresses and blockchain data. It generates you a list of specific instructions for going about claiming them including generating the commands you need to run. It helps you keep organized through complicated claiming tasks by storing a save file which can be kept on an encrypted USB drive or SD card. It also provides tools for scraping block explorers and SPV providers of particular coins to help locate balances.

This project is affiliated with [Forkdrop.io](https://forkdrop.io) however it is licensed under the MIT for private use. We greatly appreciate any feedback, feature requests bug reports, contributions and [donations](https://forkdrop.io/why-should-i-donate-to-forkdrop).

Warning
=======

At present, this is still new software. We are still working on improvements.

These scripts do not access your private keys, but merely help getting you prepared and organized for using your private keys with another tool to transact.

Documentation
==============

This is only a very brief overview, we suggest seeing our more detailed and screenshot-illustrated guides linked from the [the forkdrop.io page](https://forkdrop.io/suite) to help you get started.

Transacting
===========

This set of scripts generates instructions for using the [bitcoin\_fork\_claimer](https://github.com/ymgve/bitcoin_fork_claimer) tool which is not affiliated with this project. The Forkdrop Suite software does not handle your private keys, but rather prepares you for using your private keys with the [bitcoin\_fork\_claimer](https://github.com/ymgve/bitcoin_fork_claimer) for transacting.


claim-prep.py
=============

This tool takes a list of public addresses and queries [blockchain.info's onion gateway](https://blockchainbdgpzk.onion) to obtain the balances that the addresses may have held during relevant periods for getting credited with fork and airdrop value.

The output is a generated report detailing which coins have been credited along with a long, detailed list of tailored instructions for claiming the value over Tor by providing the private key to the [bitcoin\_fork\_claimer](https://github.com/ymgve/bitcoin_fork_claimer) tool with the appropriate wrapper.

direct-query-claim-prep.py
==========================

Rather than querying [blockchain.info's onion gateway](https://blockchainbdgpzk.onion), which is general information that can infer fork and airdrop value. This tool can query a subset of coin's SPV nodes and block explorers to obtain more specific balance info (but is less reliable than the non-coin-specific info on blockchain.info). It also generates a report of tailored instructions for claiming the value of this coin.

Also, since this has to exit Tor, this method is possibly less private due to understood de-anonymization attacks on Tor.

At present, only a small subset of coins have support implemented. These are the set of coins which are airdrops (such that the blockchain.info data is not adequate) and have some degree of market acceptance and ability to claim.

Plugins for more coins beyond this set could be implemented in the future.


mark-claimed.py
===============

A script for marking particular pieces of value as claimed using a stored save file. This allows subsequent runs of `claim-prep.py` and `direct-query-claim-prep.py` to display these coins as already claimed such that the generated reports can focus on unclaimed value.

convert-addr.py
===============

A utility for converting a Bitcoin (BTC) addresses with the Bitcoin prefixes into a corresponding equivalent address of another coin which has modified the prefix.

sync-forkdrop-data.py
=====================

This repository provides the relevant dataset from [Forkdrop.io](https://forkdrop.io) for offline private use by the scripts, however it is frozen at the time of the last update of the file in this branch. The dataset changes over time on the live website.

This script pulls down the current dataset from the site over Tor and overwrites the local copy.
