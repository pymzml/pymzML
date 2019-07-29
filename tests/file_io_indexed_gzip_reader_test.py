#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
import os
from pymzml.utils.GSGR import GSGR
import unittest
import test_file_paths


class GSGRTest(unittest.TestCase):
    """
    """

    def setUp(self):
        paths = test_file_paths.paths
        self.Reader = GSGR(paths[2])

    def test_init(self):
        """
        """
        self.assertTrue(self.Reader.indexed)

    def test_check_magic_bytes(self):
        """
        """
        self.assertTrue(self.Reader._check_magic_bytes())

    def test_read_block(self):
        block = self.Reader.read_block(2)

    def test_read_basic_header(self):
        self.Reader._read_basic_header()
        self.assertEqual(self.Reader.cm, 8)
        self.assertEqual(self.Reader.flg, 16)
        self.assertEqual(self.Reader.xfl, 2)
        self.assertEqual(self.Reader.os, 3)

    def test_read_index(self):
        self.Reader._read_index()
        self.assertTrue(self.Reader.indexed)
        self.assertEqual(self.Reader.idx_len, 6)
        self.assertEqual(self.Reader.offset_len, 6)
        self.assertIsNotNone(self.Reader.index)


if __name__ == "__main__":
    unittest.main(verbosity=3)
