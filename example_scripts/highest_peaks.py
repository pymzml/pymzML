#!/usr/bin/env python

import pymzml
from collections import defaultdict as ddict
import os


def main():
    """
    Testscript to isolate the n-highest peaks from an example file.

    Usage:

        ./highest_peaks.py

    Parses the file '../tests/data/example.mzML' and extracts the 2 highest
    intensities from each spectrum.

    """
    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    run = pymzml.run.Reader(example_file)
    highest_i_dict = ddict(list)

    number_of_peaks_to_extract = 2

    for spectrum in run:
        # print( spectrum.ID )
        if spectrum.ms_level == 1:
            for mz, i in spectrum.highest_peaks(number_of_peaks_to_extract):
                highest_i_dict[spectrum.ID].append(i)
    for spectrum_id, highest_peak_list in highest_i_dict.items():
        assert len(highest_peak_list) == number_of_peaks_to_extract
        print(
            "Spectrum {0}; highest intensities: {1}".format(
                spectrum_id, highest_peak_list
            )
        )


if __name__ == "__main__":
    main()
