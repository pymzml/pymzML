#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
import os
from pymzml.file_classes.standardGzip import StandardGzip
import unittest
import random
from pymzml.spec import Spectrum, Chromatogram
import re
import struct
import test_file_paths


class StandardGzipTest(unittest.TestCase):
    """"
    """

    def setUp(self):
        """
        """
        paths = test_file_paths.paths
        self.File = StandardGzip(paths[1], "latin-1")

    def tearDown(self):
        """
        """
        self.File.close()

    def test_getitem_5(self):
        """
        """
        ID = 5
        spec = self.File[ID]
        self.assertIsInstance(spec, Spectrum)
        self.assertEqual(spec.ID, ID)

    def test_getitem_tic(self):
        ID = "TIC"
        chrom = self.File[ID]
        self.assertIsInstance(chrom, Chromatogram)
        self.assertEqual(chrom.ID, ID)


if __name__ == "__main__":
    unittest.main(verbosity=3)
