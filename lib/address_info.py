# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

###############################################################################
# per-addresss data
###############################################################################

class AddressInfo(dict):
    def __init__(self, wd, addr):
        super().__init__()
        self.addr = addr
        self.wd = wd
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
        self['addr'] = self.addr
        self['p2sh_p2wpkh'] = self.addr[:1] == "3"
        self['bech32'] = self.addr[:3] == "bc1"


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
