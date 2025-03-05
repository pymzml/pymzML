#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pymzml


def main(mzml_file):
    """
    Example script demonstrating how to access both spectra and chromatograms
    using pymzML.

    Usage:
        ./access_spectra_and_chromatograms.py <path_to_mzml_file>
    """
    print("Initializing Reader...")
    # Initialize with skip_chromatogram=False to include chromatograms during iteration
    run = pymzml.run.Reader(mzml_file, skip_chromatogram=False)
    
    # Access the first spectrum using indexing (traditional way)
    print("\nAccessing first spectrum using indexing (run[0]):")
    try:
        spectrum = run[0]
        print(f"Spectrum ID: {spectrum.ID}")
        print(f"MS Level: {spectrum.ms_level}")
        print(f"Retention Time: {spectrum.scan_time_in_minutes()} minutes")
        print(f"Number of peaks: {len(spectrum.peaks('raw'))}")
    except Exception as e:
        print(f"Error accessing spectrum: {e}")
    
    # Access the first spectrum using the new get_spectrum method
    print("\nAccessing first spectrum using get_spectrum(0):")
    try:
        spectrum = run.get_spectrum(0)
        print(f"Spectrum ID: {spectrum.ID}")
        print(f"MS Level: {spectrum.ms_level}")
        print(f"Retention Time: {spectrum.scan_time_in_minutes()} minutes")
        print(f"Number of peaks: {len(spectrum.peaks('raw'))}")
    except Exception as e:
        print(f"Error accessing spectrum: {e}")
    
    # Access the TIC chromatogram using string identifier
    print("\nAccessing TIC chromatogram using run['TIC']:")
    try:
        chromatogram = run["TIC"]
        print(f"Chromatogram ID: {chromatogram.ID}")
        print(f"Number of data points: {len(chromatogram.peaks())}")
        
        # Print the first few data points
        print("\nFirst 5 data points (time, intensity):")
        for i, (time, intensity) in enumerate(chromatogram.peaks()):
            if i >= 5:
                break
            print(f"  {time:.4f}, {intensity:.2f}")
    except Exception as e:
        print(f"Error accessing chromatogram: {e}")
    
    # Access the first chromatogram using the new get_chromatogram method
    print("\nAccessing first chromatogram using get_chromatogram(0):")
    try:
        chromatogram = run.get_chromatogram(0)
        print(f"Chromatogram ID: {chromatogram.ID}")
        print(f"Number of data points: {len(chromatogram.peaks())}")
        
        # Print the first few data points
        print("\nFirst 5 data points (time, intensity):")
        for i, (time, intensity) in enumerate(chromatogram.peaks()):
            if i >= 5:
                break
            print(f"  {time:.4f}, {intensity:.2f}")
    except Exception as e:
        print(f"Error accessing chromatogram: {e}")
    
    # Demonstrate iterating through all items (spectra and chromatograms)
    print("\nIterating through first few items (spectra and chromatograms):")
    count = 0
    for item in run:
        if count >= 5:
            break
        if isinstance(item, pymzml.spec.Spectrum):
            print(f"  Spectrum {item.ID}, MS level {item.ms_level}, RT {item.scan_time_in_minutes():.2f} min")
        elif isinstance(item, pymzml.spec.Chromatogram):
            print(f"  Chromatogram {item.ID}, {len(item.peaks())} data points")
        count += 1
    
    print("\nDone!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(main.__doc__)
        print("Please provide a path to an mzML file.")
        sys.exit(1)
    
    mzml_file = sys.argv[1]
    if not os.path.exists(mzml_file):
        print(f"Error: File '{mzml_file}' not found.")
        sys.exit(1)
    
    main(mzml_file)
