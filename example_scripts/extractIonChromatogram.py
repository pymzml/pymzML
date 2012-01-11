#!/usr/bin/env python3.2

"""
Demonstration of the extraction of a specific ion chromatogram, i.e. XIC or EIC

Example:

>>> import pymzml, get_example_file
>>> example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
>>> run = pymzml.run.Reader(example_file, MS1_Precision = 20e-6, MSn_Precision = 20e-6)
>>> timeDependentIntensities = []
>>> for spectrum in run:
...     if spectrum['ms level'] == 1:
...         matchList = spectrum.hasPeak(MASS_2_FOLLOW)
...         if matchList != []:
...             for mz,I in matchList:
...                 timeDependentIntensities.append( [ spectrum['scan time'], I , mz ])
>>> for rt, i, mz in timeDependentIntensities:
...     print('{0:5.3f}\t{1:13.4f}\t{2:10}'.format( rt, i, mz ))

"""

from __future__ import print_function
import sys
import pymzml
import get_example_file

MASS_2_FOLLOW = 810.53

def main(verbose = False):
    example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
    run = pymzml.run.Reader(example_file, MS1_Precision = 20e-6, MSn_Precision = 20e-6)
    timeDependentIntensities = []
    for spectrum in run:
        if spectrum['ms level'] == 1:
            matchList = spectrum.hasPeak(MASS_2_FOLLOW)
            if matchList != []:
                for mz,I in matchList:
                    timeDependentIntensities.append( [ spectrum['scan time'], I , mz ])
    print('RT   \ti   \tmz')
    for rt, i, mz in timeDependentIntensities:
        print('{0:5.3f}\t{1:13.4f}\t{2:10}'.format( rt, i, mz ))
    return

if __name__ == '__main__':
    main()