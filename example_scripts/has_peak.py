#!/usr/bin/env python

import pymzml
import os


def main():
    """
    Testscript to demonstrate functionality of function :py:func:`pymzml.spec.Spectrum.has_peak`

    usage:

        ./has_peak.py

    """

    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    mz_to_find = 820.7711792
    run = pymzml.run.Reader(example_file)
    for spectrum in run:
        found_peaks = spectrum.has_peak(mz_to_find)
        if found_peaks != []:
            print("Found peaks: {0} in spectrum {1}".format(found_peaks, spectrum.ID))


if __name__ == "__main__":
    main()
