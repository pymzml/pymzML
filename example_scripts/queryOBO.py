#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pymzML comes with the queryOBO.py script that can be used to interogate the OBO 
file.

Usage:

::

    $ ./example_scripts/queryOBO.py "scan time"
    MS:1000016
    scan time
    "The time taken for an acquisition by scanning analyzers." [PSI:MS]
    Is a: MS:1000503 ! scan attribute
    $ 
"""

from __future__ import print_function
import pymzml.obo
import sys
    
if __name__ == '__main__':  
    if len(sys.argv) == 1:
        print(__doc__)
        exit(1)
    obo = pymzml.obo.oboTranslator()
    arg = sys.argv[1]
    if arg.isdigit():
        print(obo['MS:{0}'.format(arg)])
    else:
        n = 0
        for lookup in obo.lookups:
            for key in lookup.keys():
                if arg in key:
                    print("#{0}".format(n))
                    print(lookup[key]['id'])
                    print(lookup[key]['name'])
                    print(lookup[key]['def'])
                    if 'is_a' in lookup[key].keys():
                        print("Is a:",lookup[key]['is_a'])
                    n += 1
    
