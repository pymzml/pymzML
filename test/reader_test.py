import pymzml
import os
from nose.tools import *
from unittest import TestCase

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'mzML_example_files')

class ReaderTest(TestCase):

    def setUp(self):
        self.msrun = pymzml.run.Reader(os.path.join(EXAMPLE_DIR, "small-1.0.0.mzml"))

    def test_reading_scan_times(self):
        eq_(self.msrun[1]['scan time'], 0.007333333333333333)
        eq_(self.msrun[2]['scan time'], 0.03816666666666667)

    # Reproduce issue
    # https://github.com/pymzml/pymzML/issues/7
    # Cannot store spectra in a list
    def test_storing_spectra(self):
        """Storing spectra in a list and accessing their attributes, random access"""
        spectra = [self.msrun[1], self.msrun[2]]
        times = [spectrum['scan time'] for spectrum in spectra]
        eq_(times, [0.007333333333333333, 0.03816666666666667])
    

    def test_next(self):
        """Storing spectra in a list and accessing their attributes, iterator"""
        spectra = []
        for spectrum in self.msrun:
            spectra.append(spectrum)
        times = [spectrum['scan time'] for spectrum in spectra[0:2]]
        eq_(times, [0.007333333333333333, 0.03816666666666667])
