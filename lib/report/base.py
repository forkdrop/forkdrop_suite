# Copyright (c) 2018 PrimeVR
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

SATOSHIS_PER_BTC = 100000000

class ReportBase(dict):
    def __init__(self, vdb):
        self.vdb = vdb
        self.nuggets = vdb['nuggets']

    def _fmt_btc_value(self, value):
        return "%0.8f" % (value / 100000000.0)

    def _forkdrop_url(self, identifier):
        return "https://forkdrop.io/%s" % identifier

    def _spans_coin(self, coin_block, span):
        if span['defunded']:
            return (span['funded']['block'] < coin_block and
                    span['defunded']['block'] >= coin_block)
        else:
            return span['funded']['block'] < coin_block

    def _section_hdr(self, title):
        return '\n'.join([("#" * 80), title, ('#' * 80)])


    def _fmt_btc(self, satoshis):
        return "%0.8f" % (satoshis / float(SATOSHIS_PER_BTC))

    def _toc(self):
        s = 0
        yield ""
        yield "Table of Contents:"
        yield ""
        for section in self._sections():
            yield "Section %s - %s" % (s, section['title'])
            s = s + 1

    def _gen_sections(self):
        toc = "\n".join(self._toc())
        s = 0
        for section in self._sections():
            yield ""
            yield self._section_hdr("Section %d - %s" % (s, section['title']))
            yield section['content'] if section['content'] else toc
            s = s + 1
        yield '=' * 80

    def _gen(self):
        for s in self._gen_sections():
            yield s

    def __str__(self):
        return "\n".join(self._gen())
