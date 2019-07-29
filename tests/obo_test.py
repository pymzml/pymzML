#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""

import sys
import os

sys.path.append(os.path.abspath("."))
import unittest
import gzip


class TestRound(unittest.TestCase):
    def _check_rounding(self, test, expected):
        assert round(test) == expected

    def test_rounding(self):
        for x, y in [(1, 1), (1.9, 2)]:
            yield self._check_rounding, x, y


class TestOboVersion(unittest.TestCase):
    """
    Test that all obo filenames match the version contained

    """

    def setUp(self):
        self.obodir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), os.pardir, "pymzml", "obo"
        )
        self.obo_files = [f for f in os.listdir(self.obodir) if f.startswith("psi-ms")]

    def _check_version(self, a, b):
        assert a == b

    def _get_file_version(self, file_path):
        v = ""
        with gzip.open(file_path, "r") as f:
            for line in f:
                if line.decode().strip().startswith("data-version"):
                    v = line.decode().split(":")[-1].strip()
                if line.decode().startswith("remark: version"):
                    v = line.decode().split(":")[-1].strip()
                    break
        return v

    def test_version(self):
        for fn in self.obo_files:
            v = self._get_file_version(os.path.join(self.obodir, fn))
            _v = fn[7:-7].strip()
            yield self._check_version, v, _v


if __name__ == "__main__":
    unittest.main(verbosity=3)
