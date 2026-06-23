#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test cases for the new properties in the Chromatogram class.
"""
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import unittest
import pymzml.run as run
from pymzml.chromatogram import Chromatogram
import test_file_paths


class ChromatogramPropertiesTest(unittest.TestCase):
    """
    Test cases for the new properties in the Chromatogram class.
    """

    def setUp(self):
        """Set up test cases."""
        self.paths = test_file_paths.paths

        # Use a file with chromatograms for testing
        # mini.chrom.mzML is at index 3
        for i, path in enumerate(self.paths):
            if "mini.chrom.mzML" in path and not path.endswith(".gz") and not path.endswith(".idx.gz"):
                self.chrom_file = path
                break
        else:
            # Fallback to a known index if the file name is not found
            self.chrom_file = self.paths[3]  # mini.chrom.mzML

        # Initialize reader with chromatograms
        self.reader = run.Reader(
            self.chrom_file, 
            skip_chromatogram=False
        )

    def test_chromatogram_type(self):
        """Test the chromatogram_type property."""
        # Get the first chromatogram
        chromatogram = self.reader.get_chromatogram(0)

        # Test that chromatogram_type is accessible
        chromatogram_type = chromatogram.chromatogram_type

        # The type might be None depending on the test file, but the property should be accessible
        self.assertIsNotNone(chromatogram, "Chromatogram should not be None")

        # Print the chromatogram type for debugging
        print(f"Chromatogram type: {chromatogram_type}")

    def test_polarity(self):
        """Test the polarity property."""
        # Get the first chromatogram
        chromatogram = self.reader.get_chromatogram(0)

        # Test that polarity is accessible
        polarity = chromatogram.polarity

        # The polarity might be None depending on the test file, but the property should be accessible
        self.assertIsNotNone(chromatogram, "Chromatogram should not be None")

        # Print the polarity for debugging
        print(f"Polarity: {polarity}")

    def test_precursor_mz(self):
        """Test the precursor_mz property."""
        # Get the first chromatogram
        chromatogram = self.reader.get_chromatogram(0)

        # Test that precursor_mz is accessible
        precursor_mz = chromatogram.precursor_mz

        # The precursor_mz might be None depending on the test file, but the property should be accessible
        self.assertIsNotNone(chromatogram, "Chromatogram should not be None")

        # Print the precursor_mz for debugging
        print(f"Precursor m/z: {precursor_mz}")

    def test_product_mz(self):
        """Test the product_mz property."""
        # Get the first chromatogram
        chromatogram = self.reader.get_chromatogram(0)

        # Test that product_mz is accessible
        product_mz = chromatogram.product_mz

        # The product_mz might be None depending on the test file, but the property should be accessible
        self.assertIsNotNone(chromatogram, "Chromatogram should not be None")

        # Print the product_mz for debugging
        print(f"Product m/z: {product_mz}")

    def test_get_chromatogram_properties(self):
        """Test the get_chromatogram_properties method."""
        # Get the first chromatogram
        chromatogram = self.reader.get_chromatogram(0)

        # Test that get_chromatogram_properties returns a dictionary
        properties = chromatogram.get_chromatogram_properties()
        
        self.assertIsInstance(properties, dict, "get_chromatogram_properties should return a dictionary")
        
        # Check that the dictionary contains the expected keys
        expected_keys = ["id", "chromatogram_type", "polarity", "precursor_mz", "product_mz"]
        for key in expected_keys:
            self.assertIn(key, properties, f"Properties dictionary should contain key '{key}'")
        
        # Print the properties for debugging
        print("Chromatogram properties:")
        for key, value in properties.items():
            print(f"  {key}: {value}")

    def test_all_chromatograms(self):
        """Test all chromatograms in the file."""
        # Get the number of chromatograms
        chrom_count = self.reader.get_chromatogram_count()

        if chrom_count is None or chrom_count == 0:
            self.skipTest("Test file does not contain chromatograms")

        print(f"\nTesting {chrom_count} chromatograms:")

        # Test each chromatogram
        for i in range(chrom_count):
            chromatogram = self.reader.get_chromatogram(i)

            # Print information about the chromatogram
            print(f"\nChromatogram {i}:")
            print(f"  ID: {chromatogram.ID}")
            print(f"  Type: {chromatogram.chromatogram_type}")
            print(f"  Polarity: {chromatogram.polarity}")
            print(f"  Precursor m/z: {chromatogram.precursor_mz}")
            print(f"  Product m/z: {chromatogram.product_mz}")

            # Verify that the chromatogram has time and intensity data
            self.assertIsNotNone(chromatogram.time, "Chromatogram should have time data")
            self.assertIsNotNone(chromatogram.i, "Chromatogram should have intensity data")
            
            # Verify that the peaks method returns data
            peaks = chromatogram.peaks()
            self.assertIsNotNone(peaks, "Chromatogram peaks should not be None")

            # Print the first few data points
            print("  First 3 data points (time, intensity):")
            for j, (time, intensity) in enumerate(peaks):
                if j >= 3:
                    break
                print(f"    {time:.4f}, {intensity:.2f}")

    def tearDown(self):
        """Clean up after tests."""
        self.reader.close()


if __name__ == "__main__":
    unittest.main(verbosity=3)
