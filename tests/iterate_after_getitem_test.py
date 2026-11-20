import os
import unittest

import pymzml.run as run


class IterateAfterRandomAccessTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "data", "example.mzML")

    def test_iteration_after_getitem_yields_all_spectra(self):
        expected = [spec.ID for spec in run.Reader(self.path)]
        reader = run.Reader(self.path)
        self.assertEqual(reader[5].ID, 5)
        self.assertEqual([spec.ID for spec in reader], expected)


if __name__ == "__main__":
    unittest.main()
