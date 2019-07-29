#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
import os
from pymzml.file_interface import FileInterface
from pymzml.file_classes.standardGzip import StandardGzip
from pymzml.file_classes.indexedGzip import IndexedGzip
from pymzml.file_classes.standardMzml import StandardMzml
import unittest
import test_file_paths


class FileInterfaceTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.paths = test_file_paths.paths
        test_file = self.paths[1]
        self.File = FileInterface(test_file, "latin-1")

    def tearDown(self):
        """
        """
        self.File.close()

    def test_init(self):
        """
        """
        self.assertIsNotNone(self.File.file_handler)

    def test_open(self):
        """
        """
        self.assertIsInstance(self.File.file_handler, StandardGzip)
        self.File.close()
        self.File = FileInterface(self.paths[0], "latin-1")
        self.assertIsInstance(self.File.file_handler, StandardMzml)
        self.File.close()
        self.File = FileInterface(self.paths[2], "latin-1")
        self.assertIsInstance(self.File.file_handler, IndexedGzip)
        self.File.close()


if __name__ == "__main__":
    unittest.main(verbosity=3)
