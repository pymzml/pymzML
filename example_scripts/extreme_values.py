#!/usr/bin/env python

import pymzml
from collections import defaultdict as ddict
import os


def main():
    """
    Testscript to fetch the extreme m/z values from each spectrum
    of an example file.

    Usage:

        ./extreme_values.py

    Parses the file '../tests/data/example.mzML' and extracts the smallest and
    largest m/z from each each spectrum.

    """
    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    run = pymzml.run.Reader(example_file)
    extreme_mz_values = {}

    number_of_mz_values = 2

    for spectrum in run:
        # print( spectrum.ID )
        if spectrum.ms_level == 1:
            extreme_mz_values[spectrum.ID] = spectrum.extreme_values("mz")

    for spectrum_id, extreme_mz_tuple in extreme_mz_values.items():
        assert len(extreme_mz_tuple) == number_of_mz_values
        print(
            "Spectrum {0}; lowest m/z: {1} highest m/z: {2}".format(
                spectrum_id, *extreme_mz_tuple
            )
        )


if __name__ == "__main__":
    main()
