# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import json

from lib.web_data import WebData
from lib.electrum_query import ElectrumQuery
from lib.stransaction import STransaction

###############################################################################

class AddressInfo(dict):
    """
    Info for a single address
    """
    def __init__(self, settings, addr):
        super().__init__()
        self.addr = addr
        self.tails = not settings.not_tails
        self.cache = settings.cache_requests
        self['addr'] = self.addr
        self['p2sh_p2wpkh'] = self.addr[:1] == "3"
        self['bech32'] = self.addr[:3] == "bc1"

###############################################################################

class ElectrumAddressInfo(AddressInfo):
    """
    Info queried for a single address from an Electrum node
    """
    def __init__(self, settings, addr):
        super().__init__(settings, addr)

        self.server = settings.electrum_server
        self.port = settings.electrum_port
        self.ssl = not settings.electrum_no_ssl
        self.eq = ElectrumQuery(self.server, self.port, ssl=self.ssl,
                                tails=self.tails, cache=self.cache)

        self.tx_block_map = self._get_tx_block_map()

        unspents = self._get_unspent_outputs()
        sts = list(self._get_stransactions(self.tx_block_map.keys()))
        fundings = list(self._get_funding(sts))
        defundings = list(self._get_defunding(sts, fundings))
        #print("tx_block_map: %s" % self.tx_block_map)
        #print("unspents: %s" % unspents)
        #print("fundings: %s" % fundings)
        #print("defundings: %s" % defundings)
        self['spans'] = self._get_spans(unspents, fundings, defundings)
        #print("spans: %s" % json.dumps(self['spans'], sort_keys=True,
        #                               indent=1))

    def _get_block(self, txid):
        return self.tx_block_map[txid]

    def _get_spans(self, unspents, fundings, defundings):
        spans = {}
        fundings = {f['txid']: f for f in fundings}
        funding_txids = set(fundings.keys())
        for u in unspents:
            assert u['tx_hash'] in funding_txids
            span_id = self._span_id(u['tx_hash'], u['value'], u['tx_pos'])
            funded = {'value':   u['value'],
                      'span_id': span_id,
                      'n':       u['tx_pos'],
                      'block':   self._get_block(u['tx_hash']),
                      'hash':    u['tx_hash']}
            spans[span_id] = {'defunded': None,
                              'funded':   funded}
        for d in defundings:
            assert d['funding_txid'] in funding_txids
            span_id = self._span_id(d['funding_txid'], d['satoshis'], d['n'])
            defunded = {'value': d['satoshis'],
                        'span_id': span_id,
                        'n':       d['n'],
                        'block':   self._get_block(d['txid']),
                        'hash':    d['txid']}
            f = fundings[d['funding_txid']]
            funded = {'value':   f['satoshis'],
                      'span_id': span_id,
                      'n':       f['n'],
                      'block':   self._get_block(f['txid']),
                      'hash':    f['txid']}
            spans[span_id] = {'defunded': defunded,
                              'funded':   funded}

        return spans

    def _span_id(self, funding_txid, value, n):
        return "%s %d %d" % (funding_txid, value, n)

    def _get_tx_block_map(self):
        q = self.eq.query("blockchain.address.get_history", self.addr)
        #print(q)
        return {r['tx_hash']: r['height'] for r in q['result']}

    def _funding_id(self, tx_hash, n):
        return "%s %s" % (tx_hash, n)

    def _get_unspent_outputs(self):
        q = self.eq.query("blockchain.address.listunspent", self.addr)
        return q['result']

    def _get_stransactions(self, txids):
        for txid in txids:
            t = self.eq.query("blockchain.transaction.get", txid)
            yield STransaction(txid, t['result'])

    def _get_funding(self, sts):
        for st in sts:
            for addr, satoshis, n in st.iter_outs():
                if addr != self.addr:
                    continue
                yield {'satoshis': satoshis,
                       'n':        n,
                       'txid':     st.txid}

    def _get_defunding(self, sts, funding):
        funding_txids = {f['txid']: f for f in funding}
        for st in sts:
            for txid, n in st.iter_ins():
                if txid not in funding_txids.keys():
                    continue
                yield {'satoshis':     funding_txids[txid]['satoshis'],
                       'n':            n,
                       'txid':         st.txid,
                       'funding_txid': txid}

###############################################################################

class BlockchainAddressInfo(AddressInfo):
    """ Info queried for a single address from blockchain.com block explorerer.         Spans of blocks that that address held coins are calculeted
    """
    def __init__(self, settings, addr):
        super().__init__(settings, addr)
        self.wd = WebData(tails=self.tails, cache=self.cache)
        self.addr_info = self.wd.fetch_addr_info(self.addr)
        ins = list(self._get_addr_ins())
        outs = list(self._get_addr_outs())
        self._validate_outs(ins, outs)
        tx_block_map = self._get_tx_block_map(ins, outs)
        for i in ins:
            i['block'] = tx_block_map[i['hash']]
        for o in outs:
            o['block'] = tx_block_map[o['hash']]
        self['spans'] = self._calc_spans(ins, outs)
        print(self['spans'])

    def _calc_spans(self, ins, outs):
        spans = {}
        out_lookup = {o['span_id']: o for o in outs}
        for i in ins:
            span_id = i['span_id']
            o = out_lookup[span_id] if span_id in out_lookup.keys() else None
            spans[span_id] = {'funded': i,
                              'defunded': o}
        return spans

    def _span_id(self, tx_index, n, value):
        return "%s %s %s" % (tx_index, n, value)

    def _validate_outs(self, ins, outs):
        # make sure data is consistent by having every out correspond to
        # a previous in.
        i_set = set(t['span_id'] for t in ins)
        o_set = set(t['span_id'] for t in outs)
        #print(i_set)
        #print(o_set)
        for o in o_set:
            assert o in i_set

    def _iter_tx_blocks(self, txes):
        hashes = [t['hash'] for t in txes]
        for h in list(set(hashes)):
            d = self.wd.fetch_tx_info(h)
            yield h, d['block_height']

    def _get_tx_block_map(self, ins, outs):
        return {h: height for h, height in
                self._iter_tx_blocks(ins + outs)}

    def _get_addr_ins(self):
        for tx in self.addr_info['txs']:
            outs = [o for o in tx['out'] if o['addr'] == self.addr]
            for o in outs:
                yield {'n':        o['n'],
                       'hash':     tx['hash'],
                       'value':    o['value'],
                       'tx_index': o['tx_index'],
                       'span_id':  self._span_id(o['tx_index'], o['n'],
                                                 o['value'])
                      }

    def _get_addr_outs(self):
        for tx in self.addr_info['txs']:
            ins = [i for i in tx['inputs'] if
                   i['prev_out']['addr'] == self.addr]
            for i in ins:
                n = i['prev_out']['n']
                value = i['prev_out']['value']
                tx_index = i['prev_out']["tx_index"]

                yield {'tx_index': tx_index,
                       'n':        n,
                       'value':    value,
                       'hash':     tx['hash'],
                       'span_id':  self._span_id(tx_index, n, value)
                      }
