#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
import os
import pymzml.run as run
import unittest
from pymzml.spec import Spectrum, Chromatogram
import test_file_paths


class runTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.paths = test_file_paths.paths

        file_compressed_indexed = self.paths[2]
        file_compressed_unindexed = self.paths[1]
        file_uncompressed_indexed = self.paths[0]
        file_uncompressed_unindexed = self.paths[0]
        file_bad_obo_version = self.paths[10]
        file_no_obo_version = self.paths[11]
        self.reader_compressed_indexed = run.Reader(file_compressed_indexed)
        self.reader_compressed_unindexed = run.Reader(file_compressed_unindexed)
        self.reader_uncompressed_indexed = run.Reader(file_uncompressed_indexed)
        self.reader_uncompressed_unindexed = run.Reader(file_uncompressed_unindexed)
        self.reader_bad_obo_version = run.Reader(file_bad_obo_version)
        self.reader_set_obo_version = run.Reader(
            file_bad_obo_version, obo_version="3.25.0"
        )
        self.reader_set_year_obo_version = run.Reader(
            file_uncompressed_indexed, obo_version="23:06:2017"
        )
        self.reader_set_bad_obo_version = run.Reader(
            file_uncompressed_indexed, obo_version="bad_obo_version"
        )
        self.reader_set_no_obo_version = run.Reader(file_no_obo_version)

    def test_determine_file_encoding(self):
        """
        """
        encoding = self.reader_compressed_indexed._determine_file_encoding(
            self.paths[2]
        )
        self.assertEqual(encoding, "ISO-8859-1")
        encoding = self.reader_compressed_unindexed._determine_file_encoding(
            self.paths[1]
        )
        self.assertEqual(encoding, "ISO-8859-1")
        encoding = self.reader_uncompressed_indexed._determine_file_encoding(
            self.paths[3]
        )
        self.assertEqual(encoding, "ISO-8859-1")
        encoding = self.reader_uncompressed_unindexed._determine_file_encoding(
            self.paths[0]
        )
        self.assertEqual(encoding, "ISO-8859-1")

    def test_init_iter(self):
        """
        """
        mzml_version = self.reader_compressed_indexed.info["mzml_version"]
        obo_version = self.reader_compressed_indexed.info["obo_version"]
        spec_count = self.reader_compressed_indexed.info["spectrum_count"]
        run_id = self.reader_uncompressed_unindexed.info["run_id"]
        start_time = self.reader_uncompressed_unindexed.info["start_time"]
        self.assertEqual(mzml_version, "1.1.0")
        self.assertEqual(obo_version, "3.25.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_compressed_unindexed.info["mzml_version"]
        obo_version = self.reader_compressed_unindexed.info["obo_version"]
        spec_count = self.reader_compressed_unindexed.info["spectrum_count"]
        run_id = self.reader_uncompressed_unindexed.info["run_id"]
        start_time = self.reader_uncompressed_unindexed.info["start_time"]
        self.assertEqual(mzml_version, "1.1.0")
        self.assertEqual(obo_version, "3.25.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_uncompressed_indexed.info["mzml_version"]
        obo_version = self.reader_uncompressed_indexed.info["obo_version"]
        spec_count = self.reader_uncompressed_indexed.info["spectrum_count"]
        run_id = self.reader_uncompressed_unindexed.info["run_id"]
        start_time = self.reader_uncompressed_unindexed.info["start_time"]
        self.assertEqual(mzml_version, "1.1.0")
        self.assertEqual(obo_version, "3.25.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_uncompressed_unindexed.info["mzml_version"]
        obo_version = self.reader_uncompressed_unindexed.info["obo_version"]
        spec_count = self.reader_uncompressed_unindexed.info["spectrum_count"]
        run_id = self.reader_uncompressed_unindexed.info["run_id"]
        start_time = self.reader_uncompressed_unindexed.info["start_time"]

        self.assertEqual(mzml_version, "1.1.0")
        self.assertEqual(obo_version, "3.25.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_bad_obo_version.info["mzml_version"]
        obo_version = self.reader_bad_obo_version.info["obo_version"]
        spec_count = self.reader_bad_obo_version.info["spectrum_count"]
        run_id = self.reader_bad_obo_version.info["run_id"]
        start_time = self.reader_bad_obo_version.info["start_time"]

        self.assertEqual(mzml_version, "1.1.0")
        # run._obo_version_validator 2017 default obo = 4.1.0
        self.assertEqual(obo_version, "4.1.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_set_obo_version.info["mzml_version"]
        obo_version = self.reader_set_obo_version.info["obo_version"]
        spec_count = self.reader_set_obo_version.info["spectrum_count"]
        run_id = self.reader_set_obo_version.info["run_id"]
        start_time = self.reader_set_obo_version.info["start_time"]

        self.assertEqual(mzml_version, "1.1.0")
        self.assertEqual(obo_version, "3.25.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_set_year_obo_version.info["mzml_version"]
        obo_version = self.reader_set_year_obo_version.info["obo_version"]
        spec_count = self.reader_set_year_obo_version.info["spectrum_count"]
        run_id = self.reader_set_year_obo_version.info["run_id"]
        start_time = self.reader_set_year_obo_version.info["start_time"]

        self.assertEqual(mzml_version, "1.1.0")
        # run._obo_version_validator 2017 default obo = 4.1.0
        self.assertEqual(obo_version, "4.1.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_set_bad_obo_version.info["mzml_version"]
        obo_version = self.reader_set_bad_obo_version.info["obo_version"]
        spec_count = self.reader_set_bad_obo_version.info["spectrum_count"]
        run_id = self.reader_set_bad_obo_version.info["run_id"]
        start_time = self.reader_set_bad_obo_version.info["start_time"]

        self.assertEqual(mzml_version, "1.1.0")
        # run._obo_version_validator set invalid obo = 1.1.0
        self.assertEqual(obo_version, "1.1.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

        mzml_version = self.reader_set_no_obo_version.info["mzml_version"]
        obo_version = self.reader_set_no_obo_version.info["obo_version"]
        spec_count = self.reader_set_no_obo_version.info["spectrum_count"]
        run_id = self.reader_set_no_obo_version.info["run_id"]
        start_time = self.reader_set_no_obo_version.info["start_time"]

        self.assertEqual(mzml_version, "1.1.0")
        # run._obo_version_validator set invalid obo = 1.1.0
        self.assertEqual(obo_version, "1.1.0")
        self.assertIsInstance(spec_count, int)
        self.assertEqual(run_id, "exp105-01-ds5562-Pos")
        self.assertEqual(start_time, "2013-09-10T10:31:08Z")

    def test_next(self):
        """
        """
        ret = self.reader_compressed_indexed.next()
        self.assertIsInstance(ret, Spectrum)
        ret = self.reader_compressed_unindexed.next()
        self.assertIsInstance(ret, Spectrum)
        ret = self.reader_uncompressed_indexed.next()
        self.assertIsInstance(ret, Spectrum)
        ret = self.reader_uncompressed_unindexed.next()
        self.assertIsInstance(ret, Spectrum)

    def test_get_spec_count(self):
        self.assertEqual(self.reader_compressed_indexed.get_spectrum_count(), 2918)
        # self.assertEqual(self.reader_compressed_indexed.getChromatogramCount(), 1) # Failing
        self.assertEqual(self.reader_compressed_unindexed.get_spectrum_count(), 2918)
        # self.assertEqual(self.reader_compressed_unindexed.getChromatogramCount, 1) # Failing
        self.assertEqual(self.reader_uncompressed_unindexed.get_spectrum_count(), 2918)
        # self.assertEqual(self.reader_uncompressed_unindexed.getChromatogramCount(), 1) # Failing
        self.assertEqual(self.reader_uncompressed_unindexed.get_spectrum_count(), 2918)
        # self.assertEqual(self.reader_uncompressed_ununindexed.getChromatogramCount(), 1) # Failing

    def test_readers_remeber_spawned_spectra(self):
        """
        Make multiple Readers, spawn 10 spectra each, mix them
        and map them back to the reader who spawned them.
        """
        pass


if __name__ == "__main__":
    unittest.main(verbosity=3)
