#!/usr/bin/env python
import sys
import pymzml
from collections import defaultdict as ddict


def main(mzml_file):
    """
    Basic example script to demonstrate the usage of pymzML. Requires a mzML
    file as first argument.

    usage:
        ./simple_parser_v2.py <path_to_mzml_file>

    Note:

        This script uses the old syntax where the MS level can be queried as a
        key (Spectrum['ms level']). The current syntax can be found in
        simple_parser.py

    """
    run = pymzml.run.Reader(mzml_file)
    # print( run[10000].keys() )
    stats = ddict(int)
    for n, spec in enumerate(run):
        print(
            "Spectrum {0}, MS level {ms_level}".format(n, ms_level=spec["ms level"]),
            end="\r",
        )
        # the old method to obtain peaks from the Spectrum class
        stats[spec.ID] = len(spec.centroidedPeaks)

    print("Parsed {0} spectra from file {1}".format(len(stats.keys()), mzml_file))
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(main.__doc__)
        exit()
    mzml_file = sys.argv[1]
    main(mzml_file)
