#!/usr/bin/env python

import os

import pymzml


def main():
    """
    Demonstration of the extraction of a specific ion chromatogram, i.e. XIC or EIC

    All intensities and m/z values for a target m/z are extracted.

    usage:

        ./extract_ion_chromatogram.py

    """

    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    run = pymzml.run.Reader(example_file)
    time_dependent_intensities = []

    MZ_2_FOLLOW = 70.06575775

    for spectrum in run:
        if spectrum.ms_level == 1:
            has_peak_matches = spectrum.has_peak(MZ_2_FOLLOW)
            if has_peak_matches != []:
                for mz, I in has_peak_matches:
                    time_dependent_intensities.append(
                        [spectrum.scan_time_in_minutes(), I, mz]
                    )
    print("RT   \ti   \tmz")
    for rt, i, mz in time_dependent_intensities:
        print("{0:5.3f}\t{1:13.4f}\t{2:10}".format(rt, i, mz))
    return


if __name__ == "__main__":
    main()
