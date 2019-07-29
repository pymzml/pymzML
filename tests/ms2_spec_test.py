import sys
import os

sys.path.append(os.path.abspath("."))
import pymzml.run as run
import unittest
import test_file_paths


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


if __name__ == "__main__":
    unittest.main(verbosity=3)
