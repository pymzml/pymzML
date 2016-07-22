#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding: utf-8
#
# pymzml
#
# Copyright (C) 2010-2013 T. Bald, J. Barth, M. Specht, C. Fufezan
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

import pymzml

class TestRun(unittest.TestCase):
    def setUp(self):
        print('file', pymzml.__file__)
        self.specs = {}
        for precision in [1e-6, 100e-6]:
            self.specs[ precision ] = pymzml.spec.Spectrum(
                measuredPrecision = precision
            )
            self.specs[ precision ].peaks = [ (1000,10), (1000.01, 10)]

    def test_peaks_are_set(self):
        spec = pymzml.spec.Spectrum(measuredPrecision=1e-6)
        spec.peaks = [(1000,10)]
        self.assertEqual( spec.mz , [1000] )

    def test_spec_has_peak_within_precision(self):
        self.assertEqual( self.specs[1e-6].hasPeak(1000.001), [(1000, 10)])
        self.assertEqual( self.specs[1e-6].hasPeak(1000.0011) , [] )
        self.assertEqual( len(self.specs[ 100e-6].hasPeak(1000)), 2 )

    def test_adding_spectra_to_empty_spec_retains_peaks(self):
        spec = pymzml.spec.Spectrum(measuredPrecision=1e-6)
        spec += self.specs[ 1e-6 ]
        self.assertEqual( self.specs[1e-6].peaks, spec.peaks )

    def test_adding_spectra(self):
        spec = pymzml.spec.Spectrum(measuredPrecision=1e-6)
        spec.peaks = [ (1000,10)]
        spec2 = pymzml.spec.Spectrum(measuredPrecision=1e-6)
        spec2.peaks = [ (1000,10)]
        spec += spec2
        print( spec , hex(id(spec)))
        self.assertEqual( round(spec.i[0],2), round(20.0, 2) )

if __name__ == '__main__':
    unittest.main()
