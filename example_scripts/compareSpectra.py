#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
"""
Compare two spectra and return the cosine distance between them.
The returned value is between 0 and 1, a returned value of 1 
represents highest similarity.

Example:

    >>> spec1 = pymzml.spec.Spectrum(measuredPrecision = 20e-5)
    >>> spec2 = pymzml.spec.Spectrum(measuredPrecision = 20e-5)
    >>> spec1.peaks = [ ( 1500,1 ), ( 1502,2.0 ), (1300,1 )]
    >>> spec2.peaks = [ ( 1500,1 ), ( 1502,1.3 ), (1400,2 )]
    >>> spec1.similarityTo( spec2 )
    0.5682164685724541
    >>> spec1.similarityTo( spec1 )
    1.0000000000000002
    
"""

from __future__ import print_function
import sys
import pymzml
import get_example_file

def main(verbose = False):
    examplemzML = get_example_file.open_example('BSA1.mzML')
    if verbose:
        print("""
        comparing specs
        """)
    run = pymzml.run.Reader(examplemzML)
    tmp = []
    for spec in run:
        if spec['ms level'] == 1:
            if verbose:
                print("Parsing spec lvl 1 has id {0}".format(spec['id']))
            tmp.append(spec.deRef())
            if len(tmp) >= 3:
                break
    if verbose:
        print("Print total number of specs collected {0}".format(len(tmp) ) )
        
        print("cosine between spec 1 & 2 is ",tmp[0].similarityTo(tmp[1]))
        print("cosine score between spec 1 & 3 is ",tmp[0].similarityTo(tmp[2]))
        print("cosine score between spec 2 & 3 is ",tmp[1].similarityTo(tmp[2]))
        
        print("cosine score between first spec against itself ",tmp[0].similarityTo(tmp[0]))
    if tmp[0].similarityTo(tmp[0]) == 1:
        return True
    else:
        return False

if __name__ == '__main__':  
    main(verbose = True)
