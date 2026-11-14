#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""

import os
import base64
import struct
import tempfile
from pymzml.file_classes.standardMzml import StandardMzml
import unittest
from pymzml.run import Reader
from pymzml.spec import Spectrum
from pymzml.chromatogram import Chromatogram
import test_file_paths


class StandardMzmlTest(unittest.TestCase):
    """ """

    def setUp(self):
        """ """
        paths = test_file_paths.paths
        self.standard_mzml = StandardMzml(paths[0], "latin-1")

    def tearDown(self):
        """ """
        self.standard_mzml.close()

    def test_getitem(self):
        """ """
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
        """ """
        spec = self.standard_mzml._interpol_search(5)
        self.assertIsInstance(spec, Spectrum)


class FirstSpectrumTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def write_mzml(self, first_id, count=3, indexed=False):
        path = os.path.join(self.tmpdir.name, "first.mzML")
        namespace = 'xmlns="http://psi.hupo.org/ms/mzml"'
        data = '<?xml version="1.0" encoding="utf-8"?>\n'
        if indexed:
            data += f"<indexedmzML {namespace}>\n"
        data += f'<mzML {namespace} version="1.1.0"><run id="r">\n'
        data += f'<spectrumList count="{count}">\n'
        offsets = []
        for index in range(count):
            # Exercise the two-ended search without a large committed fixture.
            if index:
                data += "<!--" + " " * 128000 + "-->\n"
            offsets.append(len(data.encode("utf-8")))
            data += (
                f'<spectrum index="{index}" id="index={first_id + index}" '
                'defaultArrayLength="2">\n'
                '<cvParam cvRef="MS" accession="MS:1000511" '
                'name="ms level" value="1"/>\n'
                '<binaryDataArrayList count="2">\n'
            )
            for accession, name, values in (
                ("MS:1000514", "m/z array", (100.0, 200.0)),
                ("MS:1000515", "intensity array", (index + 1.0, index + 2.0)),
            ):
                payload = base64.b64encode(struct.pack("<2d", *values)).decode()
                data += (
                    f'<binaryDataArray encodedLength="{len(payload)}">\n'
                    '<cvParam cvRef="MS" accession="MS:1000523" '
                    'name="64-bit float"/>\n'
                    '<cvParam cvRef="MS" accession="MS:1000576" '
                    'name="no compression"/>\n'
                    f'<cvParam cvRef="MS" accession="{accession}" name="{name}"/>\n'
                    f"<binary>{payload}</binary></binaryDataArray>\n"
                )
            data += "</binaryDataArrayList></spectrum>\n"
        data += "</spectrumList></run></mzML>\n"
        if indexed:
            index_offset = len(data.encode("utf-8"))
            data += '<indexList count="1"><index name="spectrum">\n'
            for index, offset in enumerate(offsets):
                data += f'<offset idRef="index={first_id + index}">{offset}</offset>\n'
            data += "</index></indexList>\n"
            data += f"<indexListOffset>{index_offset}</indexListOffset></indexedmzML>\n"
        with open(path, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(data)
        return path

    def check_order(self, order, count=3):
        for first_id in (0, 101):
            for indexed in (False, True):
                with self.subTest(first_id=first_id, indexed=indexed):
                    path = self.write_mzml(first_id, count, indexed)
                    with Reader(path) as reader:
                        for index in order:
                            spectrum = reader[first_id + index]
                            self.assertEqual(spectrum.ID, first_id + index)
                            self.assertEqual(list(spectrum.mz), [100.0, 200.0])
                            self.assertEqual(
                                list(spectrum.i), [index + 1.0, index + 2.0]
                            )

    def test_first_and_repeated_reads(self):
        self.check_order((0, 0, 1, 2, 0))

    def test_first_after_last(self):
        self.check_order((2, 0))

    def test_single_spectrum(self):
        self.check_order((0, 0), count=1)

    def test_nonfirst_spectra(self):
        self.check_order((2, 1, 2))

    def test_out_of_range(self):
        for first_id in (0, 101):
            with self.subTest(first_id=first_id):
                path = self.write_mzml(first_id)
                with Reader(path) as reader:
                    for index in (first_id - 1, first_id + 3):
                        with self.assertRaisesRegex(
                            Exception, "Spectrum ID should be between"
                        ):
                            reader[index]


if __name__ == "__main__":
    unittest.main(verbosity=3)
