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
import subprocess as sub
import os

import pymzml

class TestRun(unittest.TestCase):

    def setUp(self):
        pass

    def test_regex(self):
      print ("Running tests") 
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
