#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
# encoding: utf-8
#
# pymzml
#
# Copyright (C) 2010-2013 T. Bald, J. Barth, M. Specht, C. Fufezan, H. Roest
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
from nose.plugins.attrib import attr

import pymzml


class TestReadChromatogram(unittest.TestCase):

    def setUp(self):
        self.dirname = os.path.dirname(os.path.abspath(__file__))
        self.datadir = os.path.join(self.dirname, "data")
        self.mini_chrom_file = os.path.join(self.datadir, "mini.chrom.mzML")
        self.chromatogram_id = "4092_IEVLDYQAGDEAGIK/2_y7"
        # Second file
        self.mini_numpress_file = os.path.join(self.datadir, "mini_numpress.chrom.mzML")
        self.numpress_chrom_id = "some_test_id"

    def check_file(self, run):
        all_chromatograms = list(run)
        self.assertEqual(len(all_chromatograms), 3)
        self.assertEqual(run.getChromatogramCount(), len(all_chromatograms))
        self.assertEqual(run.getSpectrumCount(), 0)

        chrom = run[self.chromatogram_id]

        # Chromatogram/spectrum counts should not change by random access
        self.assertEqual(run.getChromatogramCount(), len(all_chromatograms))
        self.assertEqual(run.getSpectrumCount(), 0)

        self.assertEqual(len(chrom.peaks), 176)
        self.assertAlmostEqual(sum(chrom.i), 13374.0)

        self.assertAlmostEqual(chrom.i[0], 30.0)
        self.assertAlmostEqual(chrom.i[-1], 140.0)
        self.assertAlmostEqual(chrom.time[0], 3357.62)
        self.assertAlmostEqual(chrom.time[-1], 3955.05)

    def test_readfile(self):
        run = pymzml.run.Reader(self.mini_chrom_file)
        self.assertFalse(run.info['seekable'])

        self.check_file(run)

    def test_readfile_with_index(self):
        run = pymzml.run.Reader(self.mini_chrom_file, build_index_from_scratch=True)
        self.assertTrue(run.info['seekable'])

        self.check_file(run)

    @attr('numpress')
    def test_read_numpress(self):
        run = pymzml.run.Reader(
            self.mini_numpress_file,
            obo_version = '3.51.0'
        )
        self.assertFalse(run.info['seekable'])

        all_chromatograms = list(run)
        self.assertEqual(len(all_chromatograms), 1)

        chrom = run[self.numpress_chrom_id]

        self.assertEqual(len(chrom.peaks), 176)
        self.assertAlmostEqual(sum(chrom.i), 3657.0)

        self.assertAlmostEqual(chrom.i[0], 0.0)
        self.assertAlmostEqual(chrom.i[-1], 28.0)
        self.assertAlmostEqual(chrom.time[0], 2302.530)
        self.assertAlmostEqual(chrom.time[-1], 2899.960000343)

if __name__ == '__main__':
    unittest.main()
