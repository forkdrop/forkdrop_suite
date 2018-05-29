# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import sys
import hashlib
from binascii import hexlify, unhexlify

from lib.forkdrop_info import ForkdropInfo

###############################################################################
# info for each fork coin
###############################################################################

FORK_INFO = {f['id']: f for f in ForkdropInfo()['bitcoin']}

FORK_INFO['bitcoin'] = {"prefix_p2pkh": [0],
                        "prefix_p2sh":  [5]}

###############################################################################
# convert an address to a specific coin's address
###############################################################################

BASE58_DIGITS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

class ConvertedAddress(object):
    def __init__(self, address, symbol):
        if symbol not in FORK_INFO.keys():
            sys.exit("cannot convert %s" % symbol)
        self.symbol = symbol
        self.address = address

    def _decode(self, s):
        if not s:
            return b''
        n = 0
        for c in s:
            n *= 58
            if c not in BASE58_DIGITS:
                sys.exit("invald base58")
            digit = BASE58_DIGITS.index(c)
            n += digit
        h = '%x' % n
        if len(h) % 2:
            h = '0' + h
        res = unhexlify(h.encode('utf8'))
        pad = 0
        for c in s[:-1]:
            if c == BASE58_DIGITS[0]:
                pad += 1
            else:
                break
        return b'\x00' * pad + res

    def _encode(self, b):
        n = int('0x0' + hexlify(b).decode('utf8'), 16)
        res = []
        while n > 0:
            n, r = divmod(n, 58)
            res.append(BASE58_DIGITS[r])
        res = ''.join(res[::-1])
        pad = 0
        for c in b:
            if c == 0:
                pad += 1
            else:
                break
        return BASE58_DIGITS[0] * pad + res

    def _prefix_slice(self, bs):
        return bs[0:1]

    def _hash160_slice(self, bs):
        return bs[1:-4]

    def _checksum_slice(self, bs):
        return bs[-4:]

    def _calc_checksum(self, byte_val):
        return hashlib.sha256(hashlib.sha256(byte_val).digest()).digest()[0:4]

    def _decompose_addr(self, address_str):
        b = self._decode(address_str)
        prefix = self._prefix_slice(b)
        hash160 = self._hash160_slice(b)
        checksum = self._checksum_slice(b)
        assert checksum == self._calc_checksum(prefix + hash160)
        assert len(prefix) == 1
        assert prefix[0] == 0x0 or prefix[0] == 0x5
        return prefix[0], hash160, checksum

    def _compose_fork_addr(self, btc_prefix, hash160, symbol):
        prefix_tgt = (FORK_INFO[symbol]['prefix_p2pkh'] if btc_prefix == 0x0
                      else FORK_INFO[symbol]['prefix_p2sh'])
        body = bytes(prefix_tgt) + hash160
        checksum = self._calc_checksum(body)
        return self._encode(body + checksum)

    def _convert_address(self):
        p, h, _ = self._decompose_addr(self.address)
        return self._compose_fork_addr(p, h, self.symbol)

    def __str__(self):
        return self._convert_address()

###############################################################################
# generate a report for an address
###############################################################################

class ConvertReport(object):
    def __init__(self, address):
        self.address = address

    def _iter_conversion_lines(self):
        for info in ForkdropInfo()['bitcoin']:
            if info['bfc_support'] == 'no':
                continue
            converted = str(ConvertedAddress(self.address, info['id']))
            name = "%s (%s)" % (info['name'], info['ticker'])
            yield "%-25s %s" % (name, converted)

    def __str__(self):
        return "\n".join(self._iter_conversion_lines())

###############################################################################
# tests
###############################################################################

TEST_1_ADDR = "1MrpoVBweTnwPTase83S13LSZZ2Ga4Amk7"
TEST_1 = {
    "bitcoin":           "1MrpoVBweTnwPTase83S13LSZZ2Ga4Amk7",
    "big-bitcoin":       "BRJuRCe9PyNqqJ53FcNQ8B97JATrMmQeGW",
    "bitcoin-hush":      "RW91t15EFHbWTTx57J2Z6ZfeKpUsEJtSBE",
    "bitcoin-faith":     "Fr2YFPvKCxUUq4bzXE2uTZ8mDiJE8mCMqc",
    "bitcoin-world":     "WjXrgQwyUdcu66mCRkMhQCCsWNq8SeCbpw",
    "bitcoin-gold":      "GehkDcWtdKQETvtAa4hYRogLUip7dYBiRj",
    "bitcoinx":          "XYD4edYYtzYeiy3NUb2LNSkSmPM1wUjhyN",
    "bitcoin-pizza":     "PVSzxTanhPH8NJFdzCMxfwJiBJC9j8nXaS",
    "bitcoin-hot":       "HTNxBq7U3gKz6oALcuNBQ4DujjL13d9pHB",
    "bitcoin-pay":       "PtnbwZt5QZk1BjPj1chHA4aVooT6MRVu2K",
    "bitcoin-candy":     "CdKiNXY1XWmUHbVJKsNMaYxUBgEgUP2Vwd",
    "bitcoin-community": "Si9pqKy6Npz8umNLBZ2WYwV1DLFhRhPmVA",
    "bitcoin-private":   "b1RL2Ug2wPcq3WjuSbGUQbYK8BpjLtZzfXu",
    "bitcoin-atom":      "AcdhSz3ZycT6CRnsCmhm9vbY39wxzBC219",
    "bitcoin-interest":  "iQLMEZbL4s4Jofoi8v1wTq6gm1JV4q1q9w",
    "bitcoin-god":       "gPeLK26tWxjviW7H1pMM3CjkcV1mYRhob3",
}

TEST_2_ADDR = "3D6hWQDdjFFzGtkYggcBCSk3MuTF55TGoj"
TEST_2 = {
    "bitcoin":           "3D6hWQDdjFFzGtkYggcBCSk3MuTF55TGoj",
    "big-bitcoin":       "bQ8xH64gXgL5hZuUeFFfzUWyiG4hwcazML",
    "bitcoin-hush":      "bQ8xH64gXgL5hZuUeFFfzUWyiG4hwcazML",
    "bitcoin-faith":     "HHvoyCeiaZUeu4daYNGLAqGaPZUFtyXdNH",
    "bitcoin-world":     "DftP7Dy8BwJmYANoKbGTohpVj29mbV3HQi",
    "bitcoin-gold":      "ATBZEMapWVbkzhG78EbuvheCgz6DsKyx2k",
    "bitcoinx":          "SYhgchWLui8oi2qa71vfKiXfsAPxLVsGwC",
    "bitcoin-pizza":     "ZPSwMYaEyn1hcQD3X9b5ZrA3ZjmzLU7nLG",
    "bitcoin-hot":       "3D6hWQDdjFFzGtkYggcBCSk3MuTF55TGoj",
    "bitcoin-pay":       "3D6hWQDdjFFzGtkYggcBCSk3MuTF55TGoj",
    "bitcoin-candy":     "cc9mEQxYfDii9sKjiWFdSrLLbmqY42mHc5",
    "bitcoin-community": "QY1fhA1uMopRcs98yvG4u6Ajie7EmFQjxR",
    "bitcoin-private":   "bxnX892hwuPvdApcdtdLYHcvMhGRmvhGrJA",
    "bitcoin-atom":      "5DniRwi5H9aNN4SyonGmd56yWRjxeoHn8R",
    "bitcoin-interest":  "ATBZEMapWVbkzhG78EbuvheCgz6DsKyx2k",
    "bitcoin-god":       "ATBZEMapWVbkzhG78EbuvheCgz6DsKyx2k",
}

if __name__ == '__main__':
    for symbol, answer in TEST_1.items():
        if not str(ConvertedAddress(TEST_1_ADDR, symbol)) == answer:
            sys.exit("bad TEST_1 result %s" % symbol)
        print("%30s %20s -> %30s" % (TEST_1_ADDR, symbol, answer))
    for symbol, answer in TEST_2.items():
        if not str(ConvertedAddress(TEST_2_ADDR, symbol)) == answer:
            sys.exit("bad TEST_2 result %s" % symbol)
        print("%30s %20s -> %30s" % (TEST_2_ADDR, symbol, answer))
