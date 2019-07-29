import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pymzml.run as run

try:
    import numpy as np
except:
    np = None
import unittest
import test_file_paths


class ChromatogramTest(unittest.TestCase):
    def assertPeaksIdentical(self, peaks1, peaks2, msg=None):
        self.assertEqual(
            len(peaks1), len(peaks2)
        )  # , msg='List have different number of peaks!')
        for x in range(len(peaks1)):
            self.assertCountEqual(peaks1[x], peaks2[x], msg=msg)

    def setUp(self):
        self.paths = test_file_paths.paths
        path = self.paths[2]
        self.Run_np = run.Reader(path)
        self.chrom = self.Run_np["TIC"]

    def test_time(self):
        time = self.chrom.time
        mz = self.chrom.mz
        self.assertCountEqual(time, mz)
        intensity = self.chrom.i

    def test_i(self):
        self.chrom.profile = [(1, 10), (2, 20), (3, 30)]
        peaks = self.chrom.peaks()
        print(self.chrom.peaks())
        self.assertPeaksIdentical(peaks, [(1, 10), (2, 20), (3, 30)])

    def test_profile(self):
        profile = self.chrom.profile
        self.assertIsNotNone(len(profile))
        if np:
            self.assertIsInstance(profile, np.ndarray)
        else:
            self.assertIsInstance(profile, list)


if __name__ == "__main__":
    unittest.main(verbosity=3)
