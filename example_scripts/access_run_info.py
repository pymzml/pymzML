#!/usr/bin/env python
import sys
import pymzml


def main(mzml_file):
    """
    Basic example script to access basic run info of an mzML file. Requires a
    mzML file as first command line argument.

    usage:

        ./access_run_info.py <path_to_mzml_file>

    >>> run.info =
            {
                'encoding': 'utf-8',
                 'file_name': '/Users/joe/Dev/pymzml_2.0/tests/data/BSA1.mzML.gz',
                 'file_object': <pymzml.file_interface.FileInterface object at 0x1039a3f28>,
                 'obo_version': '1.1.0',
                 'offset_dict': None,
                 'run_id': 'ru_0',
                 'spectrum_count': 1684,
                 'start_time': '2009-08-09T22:32:31'
             }

    """
    run = pymzml.run.Reader(mzml_file)
    print(
        """
Summary for mzML file:
    {file_name}
Run was measured on {start_time} using obo version {obo_version}
File contains {spectrum_count} spectra
        """.format(
            **run.info
        )
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(main.__doc__)
        exit()
    mzml_file = sys.argv[1]
    main(mzml_file)
