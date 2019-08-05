#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
import os
from pymzml.file_classes.standardMzml import StandardMzml
import unittest
from pymzml.spec import Spectrum, Chromatogram
import test_file_paths


class StandardMzmlTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.paths = test_file_paths.paths
        self.standard_mzml = StandardMzml(self.paths[0], "latin-1")

    def tearDown(self):
        """
        """
        self.standard_mzml.close()

    def test_getitem(self):
        """
        """
        ID = 8
        spec = self.standard_mzml[ID]
        self.assertIsInstance(spec, Spectrum)
        target_ID = spec.ID
        self.assertEqual(ID, target_ID)

        ID = "TIC"
        chrom = self.standard_mzml[ID]
        self.assertIsInstance(chrom, Chromatogram)
        self.assertEqual(ID, chrom.ID)

    def test_interpol_search(self):
        """
        """
        spec = self.standard_mzml._interpol_search(5)
        self.assertIsInstance(spec, Spectrum)

    def test_build_index(self):
        standard_mzml = StandardMzml(
            self.paths[0], "latin-1", build_index_from_scratch=False
        )
        print(standard_mzml.offset_dict)
        assert len(standard_mzml.offset_dict) == 11
        for x in range(1, 11):
            assert x in standard_mzml.offset_dict
        assert standard_mzml.offset_dict['TIC" info="just any number since not existent, ja'] == (132417,)


    def test_build_index_from_scratch(self):
        standard_mzml = StandardMzml(self.paths[11], 'latin-1', build_index_from_scratch=True)
        assert len(standard_mzml.offset_dict) == 12
        print(standard_mzml.offset_dict)
        for x in range(1, 11):
            assert x in standard_mzml.offset_dict


    def test_build_index_from_scratch_chromo_file(self):
        standard_mzml = StandardMzml(self.paths[3], 'latin-1', build_index_from_scratch=True)
        assert len(standard_mzml.offset_dict) == 3
        exp_chromo_names = [
            "DECOY_24891_FLEQHGVNFQEINIDEHPEK/3_y6",
            "4092_IEVLDYQAGDEAGIK/2_y7",
            "54036_LEKELEEKKEALELAIDQASR/3_y6",
        ]
        for x in exp_chromo_names:
            assert x in standard_mzml.offset_dict



if __name__ == "__main__":
    unittest.main(verbosity=3)
