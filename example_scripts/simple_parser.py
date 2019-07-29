#!/usr/bin/env python
import sys
import pymzml


def main(mzml_file):
    """
    Basic example script to demonstrate the usage of pymzML. Requires a mzML 
    file as first argument.

    usage:
    
        ./simple_parser.py <path_to_mzml_file>

    Note:

        This script uses the new syntax with the MS level being a property of
        the spectrum class ( Spectrum.ms_level ). The old syntax can be found in
        the script simple_parser_v2.py where the MS level can be queried as a key
        (Spectrum['ms level'])


    """
    run = pymzml.run.Reader(mzml_file)
    for n, spec in enumerate(run):
        print(
            "Spectrum {0}, MS level {ms_level} @ RT {scan_time:1.2f}".format(
                spec.ID, ms_level=spec.ms_level, scan_time=spec.scan_time_in_minutes()
            )
        )
    print("Parsed {0} spectra from file {1}".format(n, mzml_file))
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(main.__doc__)
        exit()
    mzml_file = sys.argv[1]
    main(mzml_file)
