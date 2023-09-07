#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""

import sys
import os
import pymzml.regex_patterns as rp
import unittest
from collections import OrderedDict as odict
import re


class RegexTest(unittest.TestCase):
    def setUp(self):

        spec_OBO_1_1_0 = (
            b'<spectrum id="spectrum=1019" index="8" defaultArrayLength="431">'
        )
        spec_OBO_1_1_0 = b'<spectrum id="scan=3" index="0" sourceFileRef="SF1" defaultArrayLength="92">'
        spec_OBO_1_0_0 = (
            b'<spectrum index="317" id="S318" nativeID="318" defaultArrayLength="34">'
        )
        spec_OBO_0_99_1 = b'<spectrum id="S20" scanNumber="20" msLevel="2">'

        chro_OBO_1_1_0 = ""
        chro_OBO_1_1_0 = ""
        chro_OBO_1_0_0 = ""
        chro_OBO_0_99_1 = ""

        self.spec_tags = odict(
            [
                ("OBO_1_1_0", spec_OBO_1_1_0),
                ("OBO_1_1_0", spec_OBO_1_1_0),
                ("OBO_1_0_0", spec_OBO_1_0_0),
                ("OBO_0_99_1", spec_OBO_0_99_1),
            ]
        )

        self.chro_tags = odict(
            [
                ("OBO_1_1_0", chro_OBO_1_1_0),
                ("OBO_1_1_0", chro_OBO_1_1_0),
                ("OBO_1_0_0", chro_OBO_1_0_0),
                ("OBO_0_99_1", chro_OBO_0_99_1),
            ]
        )

    def test_spectrum_id_patter(self):
        for tag in self.spec_tags.values():
            self.assertRegex(tag.decode("utf-8"), rp.SPECTRUM_ID_PATTERN)

    # def test_spectrum_open_patter(self):
    #     for tag in self.spec_tags.values():
    #         print('tag', tag, rp.SPECTRUM_OPEN_PATTERN)
    #         self.assertRegex(
    #             tag,
    #             rp.SPECTRUM_OPEN_PATTERN
    #         )

    def test_spectrum_tag_patter(self):
        for tag in self.spec_tags.values():
            self.assertRegex(tag.decode("utf-8"), rp.SPECTRUM_TAG_PATTERN)

    def test_index_and_id_order_does_not_matter(self):
        a = b'<spectrum id="controllerType=0 controllerNumber=1 scan=1" index="0" defaultArrayLength="1100">'
        b = b'<spectrum index="0" id="controllerType=0 controllerNumber=1 scan=1" defaultArrayLength="917">'
        a_match = re.search(rp.SPECTRUM_OPEN_PATTERN, a).groups()
        b_match = re.search(rp.SPECTRUM_OPEN_PATTERN, b).groups()
        a_dict = dict(zip(a_match[0::2], a_match[1::2]))
        b_dict = dict(zip(b_match[0::2], b_match[1::2]))
        assert a_dict == b_dict


if __name__ == "__main__":
    unittest.main(verbosity=3)
