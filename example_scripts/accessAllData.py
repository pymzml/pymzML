#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
accessAllData.py

Demos the usage of the spectrum.xmlTree iterator
that can be used to extract all MS:tag for a given
spectrum.

Example:


>>> example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
>>> run = pymzml.run.Reader(example_file, MSn_Precision = 250e-6)
>>> spectrum = run[1]
>>> for element in spectrum.xmlTree:
...     print('-'*40)
...     print(element)
...     print(element.get('accession') )
...     print(element.tag)
...     print(element.items())

"""

from __future__ import print_function
import pymzml
import get_example_file

def main(verbose = False):
    example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
    run = pymzml.run.Reader(example_file, MSn_Precision = 250e-6)
    spectrum = run[1]
    if verbose:
        print(spectrum['id'], spectrum['ms level'])
    for element in spectrum.xmlTree:
        if verbose:
            print('-'*40)
            print(element)
            print(element.get('accession') )
            print(element.tag)
            print(element.items())
    
    return True
    
if __name__ == '__main__':
    main(verbose = True)
