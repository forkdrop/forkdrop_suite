# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

from lib.utl.constants import SATOSHIS_PER_BTC
from lib.web_data import WebData
from xml.etree import ElementTree as ET

def bitcoin_cbc_coin_amount(satoshis):
    # airdrops to addresses > 1.0
    btc = satoshis / float(SATOSHIS_PER_BTC)
    return (satoshis - SATOSHIS_PER_BTC) if btc >= 1.0 else 0


def bitcoin_cbc_claimer_line(n):
    src_addr = n['src_addr']
    txid = "<%s-airdrop-txid>" % src_addr
    priv_key = "%s-private-key" % n['src_addr']
    dst_addr = "bitcoin-cbc-destination-address"
    txindex = "<%s-airdrop-txindex>" % src_addr
    satoshis = "<%s-airdrop-satoshis>" % src_addr
    force = "--force " if n.bfc_force else ""
    return ("python2.7 bitcoin_fork_claimer/claimer.py BCBC %s %s %s %s"
            " %s--txindex %s --satoshis %s" %
            (txid, priv_key, src_addr, dst_addr, force, txindex, satoshis))

BITCOIN_CBC_INSTRUCTIONS = """
Bitcoin@CBC is a new blockchain that airdropped value BTC addresses as new
transactions with an amount determined by their formula. To use the
bitcoin_fork_claimer tool privately, the details of teh transactions must be
manually found and provided here.

One must use a Bitcoin@CBC node or block explorer to find:

1) The transaction hash (a.k.a transaction ID) which credits the address
2) The transaction index of the specific output
3) The amount of Bitcoin@CBC satoshis credited

This has been automated to access the Bitcoin@CBC block explorer via the
direct-query-claim-prep.py script included in forkdrop_suite. This will gather
the balances and provide a more specific report tailored to claiming Bitcoin
Private.

WARNING: These quereis are less private than blockchain.info queries and may be
less reliable.
"""

ADDR_URL = "http://be.cleanblockchain.org/address/%s"


class BitcoinCbcQuery(object):
    def __init__(self, vdb, settings):
        self.vdb = vdb
        self.coin = self.vdb.get_coin_info('bitcoin-cbc')

        self.addrs = [{'addr':        a,
                       'p2sh_p2wpkh': a[:1] == "3",
                       'bech32':      a[:3] == "bc1"}
                      for a in settings.addresses]

        self.tails = not settings.not_tails
        self.cache = settings.cache_requests
        self.bfc_force = settings.bfc_force

        self.wd = WebData(tails=self.tails, cache=self.cache)
        self._add_nuggets()

    def _slice_table(self, content):
        # kinda hacky - slices out the last html table in the content
        start = content.rfind("<table")
        end = content.rfind("</table>")
        return content[start:end] + "</table>"

    def _strip(self, td):
        # kinda hacky - gets at the internal text of a html <a> element if
        # there is one instead of just text
        if len(td.getchildren()) > 0:
            return td.getchildren()[0].text
        return td.text

    def _iter_txes(self, addr_html):
        table = self._slice_table(addr_html)
        t = ET.XML(table)
        rows = iter(t)
        headers = [col.text for col in next(rows)]
        for row in rows:
            values = [col for col in row]
            yield values[0].getchildren()[0].attrib['href']

    def _iter_tx_outputs(self, tx_html):
        table = self._slice_table(tx_html)
        t = ET.XML(table)
        rows = iter(t)
        headers = [col.text for col in next(rows)]
        for row in rows:
            values = [col for col in row]
            index = int(values[0].getchildren()[0].text)
            amount = int(float(values[2].text) * SATOSHIS_PER_BTC)
            addr = values[3].getchildren()[0].text
            yield index, amount, addr


    def _add_nuggets(self):
        for a in self.addrs:
            addr = a['addr']
            addr_url = ADDR_URL % addr
            addr_html = self.wd.fetch_web_url_text_info(addr_url)
            for tx_path in self._iter_txes(addr_html):
                txid = tx_path.split('/')[-1].split("#")[0]
                tx_url = ADDR_URL % tx_path
                tx_html = self.wd.fetch_web_url_text_info(tx_url)
                for index, satoshis, to_addr in self._iter_tx_outputs(tx_html):
                    if to_addr != addr:
                        continue
                    self.vdb['nuggets'].append_direct_query(a, self.coin, txid,
                                                            index, satoshis)


BITCOIN_CBC = {
    'id':           'bitcoin-cbc',
    'instructions': BITCOIN_CBC_INSTRUCTIONS,
    'claimer_line': bitcoin_cbc_claimer_line,
    'coin_amount':  bitcoin_cbc_coin_amount,
    'direct_query': BitcoinCbcQuery,
}
