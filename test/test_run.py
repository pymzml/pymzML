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

import pymzml

class TestRun(unittest.TestCase):
    def setUp(self):
        example_mzml_filename = os.path.join(
            os.path.dirname(__file__),
            'data',
            'example.mzml',
        )
        self.example_mzml = open(example_mzml_filename)

    def tearDown(self):
        self.example_mzml.close()

    def test_file_object(self):
        run = pymzml.run.Reader('', file_object=self.example_mzml)
        self.assertEqual(run.info['fileObject'], self.example_mzml)

    def test_read_obo_version(self):
        run = pymzml.run.Reader('', file_object=self.example_mzml)
        self.assertEqual(run.info['obo_version'], '3.25.0')

    def test_provided_obo_version(self):
        run = pymzml.run.Reader('', file_object=self.example_mzml, obo_version='1.1.0')
        self.assertEqual(run.info['obo_version'], '1.1.0')

    def test_provided_bad_obo_version(self):
        with self.assertRaises(Exception):
            run = pymzml.run.Reader('', file_object=self.example_mzml, obo_version='sad')

    def test_regex(self):
        spectrumIndexPattern = pymzml.run.RegexPatterns.spectrumIndexPattern
        simIndexPattern = pymzml.run.RegexPatterns.simIndexPattern
        line1 = b'<offset idRef="controllerType=0 controllerNumber=1 scan=1">4363</offset>'
        line2 = b'<offset idRef="S16004" nativeID="16004">236442042</offset>'
        line3 = b'<offset idRef="SIM SIC 651.5">330223452</offset>\n'

        match_spec = spectrumIndexPattern.search(line1)
        self.assertTrue(match_spec)
        self.assertEqual(match_spec.group('nativeID'), b"1")
        self.assertEqual(match_spec.group('type'), b"scan=" )
        self.assertEqual(match_spec.group('offset'), b"4363" )

        match_spec = spectrumIndexPattern.search(line2)
        self.assertTrue(match_spec)
        self.assertEqual(match_spec.group('nativeID'), b"16004")
        self.assertEqual(match_spec.group('type'), b'nativeID="')
        self.assertEqual(match_spec.group('offset'), b"236442042")

        match_sim  = simIndexPattern.search(line3)
        self.assertEqual(match_sim.group('nativeID'), b"SIM SIC 651.5")
        self.assertEqual(match_sim.group('offset'), b"330223452")



if __name__ == '__main__':
    unittest.main()
