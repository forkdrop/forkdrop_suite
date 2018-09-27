# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import json

from bitcoin.core import CTransaction, VectorSerializer
from bitcoin.core import lx, b2lx, x
from bitcoin.core.script import CScriptOp

from bitcoin.base58 import CBase58Data


###############################################################################

def coutpoint2dict(coutpoint):
    d = {}
    d['hash'] = b2lx(coutpoint.hash)
    d['n'] = coutpoint.n
    return d

def scriptstuff2dict(opcode, data, idx):
    return {'opcode':  str(CScriptOp(opcode)),
            'data':    b2lx(data) if data else None,
            'sop_idx': idx}

def cscript2dict(cscript):
    return {'script': [scriptstuff2dict(o, d, i) for o, d, i in
                       cscript.raw_iter()]}

def ctxin2dict(ctxin):
    d = {}
    d['nSequence'] = ctxin.nSequence
    d['prevout'] = coutpoint2dict(ctxin.prevout)
    d['scriptSig'] = cscript2dict(ctxin.scriptSig)
    return d

###############################################################################

def scriptpubkey2dict(scriptPubKey):
    s = cscript2dict(scriptPubKey)['script']
    if s[0]['opcode'] == "OP_HASH160":
        assert len(s) == 3, "unexpected script length"
        assert s[2]['opcode'] == 'OP_EQUAL', "unexpected scriptPubKey"
        return {'type':    "P2SH_OR_P2PKWH",
                'address': str(CBase58Data.from_bytes(lx(s[1]['data']), 5))}
    elif s[0]['opcode'] == 'OP_DUP':
        assert s[1]['opcode'] == 'OP_HASH160', "unexpected scriptPubKey"
        assert s[3]['opcode'] == 'OP_EQUALVERIFY', "unexpected scriptPubKey"
        assert s[4]['opcode'] == 'OP_CHECKSIG', "unexpected scriptPubKey"
        return {'type':    "P2PKH",
                'address': str(CBase58Data.from_bytes(lx(s[2]['data']), 0))}
    else:
        assert False, "unexpected scriptPubKey"
    # TODO bech32


def ctxout2dict(ctxout):
    d = {}
    d['nValue'] = ctxout.nValue
    d['scriptPubKey'] = scriptpubkey2dict(ctxout.scriptPubKey)
    return d

def ctxoutaddr(ctxout):
    return scriptpubkey2dict(ctxout.scriptPubKey)['address']

###############################################################################

def cscriptwitness2dict(cscriptwitness):
    return {'stack': [str(s) for s in cscriptwitness.stack]}

def ctxinwitness2dict(ctxinwitness):
    return {'scriptWitness': cscriptwitness2dict(ctxinwitness.scriptWitness)}

def ctxwitness2dict(ctxwitness):
    d = {}
    d['vtxinwit'] = [ctxinwitness2dict(w) for w in ctxwitness.vtxinwit]
    return d

###############################################################################


class STransaction(object):
    """
    Wrapper class for CTransaction for accessing contained info that is needed
    for suite operations.  """
    def __init__(self, txid, rawhex):
        self.ct = CTransaction.deserialize(x(rawhex))
        self.txid = txid

    def to_dict(self):
        d = {}
        d['nVersion'] = self.ct.nVersion
        d['nLockTime'] = self.ct.nLockTime
        d['vin'] = [ctxin2dict(i) for i in self.ct.vin]
        d['vout'] = [ctxout2dict(o) for o in self.ct.vout]
        d['wit'] = ctxwitness2dict(self.ct.wit)
        d['txid'] = self.txid
        return d

    def to_json(self):
        return json.dumps(self.to_dict(), indent=1, sort_keys=True)


    def iter_ins(self):
        for i in self.ct.vin:
            txid = b2lx(i.prevout.hash)
            n = i.prevout.n
            yield txid, n

    def iter_outs(self):
        n = 0
        for o in self.ct.vout:
            addr = ctxoutaddr(o)
            satoshis = o.nValue
            yield addr, satoshis, n
            n = n + 1
