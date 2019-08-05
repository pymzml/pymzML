import sys
import os

sys.path.append(os.path.abspath("."))
from pymzml.spec import PROTON

import pymzml.run as run
import unittest
import test_file_paths
import numpy as np


class SpectrumMS2Test(unittest.TestCase):
    """
        BSA test file

    Peptide @ 
    Scan: 2548
    RT [min] 28.96722412109367
    Selected_precursor [(443.711242675781, 0.0)]

    """

    def setUp(self):
        """
        """
        # self.paths = [
        #     os.path.join( DATA_FOLDER, file ) for file in DATA_FILES]
        self.paths = test_file_paths.paths
        path = self.paths[9]
        self.Run = run.Reader(path)
        self.spec = self.Run[2548]

    def test_scan_time(self):
        scan_time = self.spec.scan_time_in_minutes()
        self.assertIsNotNone(scan_time)
        self.assertIsInstance(scan_time, float)
        self.assertEqual(round(scan_time, 4), round(28.96722412109367, 4))

    def test_select_precursors(self):
        selected_precursor = self.spec.selected_precursors
        self.assertIsInstance(selected_precursor[0], dict)
        self.assertIsInstance(selected_precursor[0]["mz"], float)
        self.assertIsInstance(selected_precursor[0]["i"], float)
        self.assertIsInstance(selected_precursor[0]["charge"], int)
        self.assertEqual(
            selected_precursor, [{"mz": 443.711242675781, "i": 0.0, "charge": 2}]
        )

    def test_deconvolute_peaks(self):
        charge = 3
        test_mz = 430.313
        arr = np.array([(test_mz, 100), (test_mz + PROTON / charge, 49)])
        spec = self.Run[2548]
        spec.set_peaks(arr, "centroided")
        decon = spec.peaks("deconvoluted")
        self.assertEqual(len(decon), 1)
        decon_mz = (test_mz * charge) - charge * PROTON
        self.assertEqual(decon[0][0], decon_mz)
        self.assertEqual(decon[0][1], 149)  # 149 since itensities are 100 and 49
        self.assertEqual(decon[0][2], 3)


if __name__ == "__main__":
    unittest.main(verbosity=3)
