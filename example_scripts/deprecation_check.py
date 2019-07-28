#!/usr/bin/env python3

import os

import pymzml


def main():
    """
    Testscript to highlight the function name changes in the Spectrum class.

    Note:
        Please adjust any old scripts to the new syntax.

    usage:

        ./deprecation_check.py

    """

    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    run = pymzml.run.Reader(example_file)
    spectrum_list = []
    for pos, spectrum in enumerate(run):
        spectrum_list.append(spectrum)
        spectrum.hasPeak((813.19073486))
        spectrum.extremeValues("mz")
        spectrum.hasOverlappingPeak(813.19073486)
        spectrum.highestPeaks(1)
        spectrum.estimatedNoiseLevel()
        spectrum.removeNoise()
        spectrum.transformMZ(813.19073486)
        if pos == 1:
            spectrum.similarityTo(spectrum_list[0])
            break


if __name__ == "__main__":
    main()
