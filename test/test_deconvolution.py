#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
# encoding: utf-8
#
# pymzml
#
# Copyright (C) 2014 T. Bald, J. Barth, M. Specht, C. Fufezan, H. Roest
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

import sys
import unittest
import pymzml
sys.path.append('./example_scripts')
sys.path.append('../example_scripts')
import get_example_file


class TestDeconvolution(unittest.TestCase):

    def setUp(self):
        example_file = get_example_file.open_example('deconvolution.mzML.gz')
        run = pymzml.run.Reader(
            example_file,
            MS1_Precision=5e-6,
            MSn_Precision=20e-6
        )
        for spec in run:
            # there is only one spectrum, so just read this
            self.spec = spec
            break

    def check_peaklist(self, mz_range, result):
        tmp = self.spec.deRef()
        deconvoluted_peak_list = tmp.deconvolutedPeaks

        # reduce to interesting range
        tmp_deconv_peaks = [(mass, i) for mass, i in deconvoluted_peak_list
                            if mz_range[0] <= mass <= mz_range[1]]

        self.assertEqual(len(tmp_deconv_peaks), len(result))
        for pos, (mass, i) in enumerate(tmp_deconv_peaks):
            self.assertAlmostEqual(mass, result[pos][0])
            self.assertAlmostEqual(i, result[pos][1])

    def check_deconvolution_with_debug_parameter(self, mz_range, expected_result):
        tmp = self.spec.deRef()
        deconv_peaklist, masses2mz = tmp.deconvolute_peaks(debug=True)
        result = []
        for mass, results in masses2mz.items():
            if mz_range[0] < mass < mz_range[1]:
                result.append([mass, results])
        # print(result)
        # print(expected_result)
        self.assertEqual( sorted(result), sorted(expected_result))

    def check_devonvolution_intensities(self, mz_range, expected_result):
        tmp = self.spec.deRef()
        tmp.reduce(tuple(mz_range))
        self.assertEqual(tmp._get_deisotopedMZ_for_chargeDeconvolution(), expected_result)

    def test_masses(self):
        self.check_peaklist((1163, 1208), [(1190.5785115257675, 19276.015691004373)])
        # this is correct
        self.check_peaklist((1191, 1400), [(1208.5995290987673, 27546.527600749054)])
        self.check_peaklist((2300, 2500), [(2395.169033526201, 19792.568515412233)])

    def test_devonvolution_intensities(self):
        # belonging to mass 1190
        self.check_devonvolution_intensities([590, 615], [
            (596.2956063083736, 9214.135922430825, 2, 2),
            (605.3046530030003, 14551.997036341349, 2, 3),
        ])
        # belonging to mass 1190
        self.check_devonvolution_intensities([1190, 1204], [
            (1191.5876398350977, 10061.879768573546, 1, 3),
            (1198.5917932298705, 19792.568515412233, 2, 4),
        ])

    def test_deconvolution_with_debug_parameter(self):
        expected_result = [[1208.5947530724607, [(605.3046530030003, 14551.997036341349, 2, 3)]],
                           [1208.604305125074, [(1209.611581591844, 12994.530564407705, 1, 3)]]]
        self.check_deconvolution_with_debug_parameter([1208, 1210], expected_result)

        expected_result = [[2395.169033526201, [(1198.5917932298705, 19792.568515412233, 2, 4)]]]
        self.check_deconvolution_with_debug_parameter([2390, 2400], expected_result)

        expected_result = [[1190.5803633683277, [(1191.5876398350977, 10061.879768573546, 1, 3)]],
                           [1190.5766596832073, [(596.2956063083736, 9214.135922430825, 2, 2)]]]
        self.check_deconvolution_with_debug_parameter([1163, 1208], expected_result)


if __name__ == '__main__':
    unittest.main()
