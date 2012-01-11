#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple parser ... of cf playground :)

"""

from __future__ import print_function
import sys
import pymzml
import get_example_file
    
def main(verbose = False):
    file_n = 0
    
    successful = dict()
    
    for example_file in get_example_file.SHA256_DICT.keys():
        file_n += 1
        n = 1
        if verbose:
            print("{0}\t{1}\t{2}".format(file_n, n, example_file),file = sys.stderr)
        try:
            for spec in pymzml.run.Reader(get_example_file.open_example(example_file)):
                n += 1
                spec.peaks
                spec.centroidedPeaks
                spec.removeNoise('median')
                spec.hasPeak(100)
                spec.deRef()
                spec.extremeValues('mz')
                spec.extremeValues('i')
                successful[example_file] = True
        except:
            if verbose:
                raise
            successful[example_file] = False
            return False

    if verbose:
        for file in successful:
            print('{0}\t{1}'.format(file, successful[file]))
    return True
        
if __name__ == '__main__':
    main(verbose = True)
