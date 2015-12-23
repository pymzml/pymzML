#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test of the mzML writing functionality.

This is very preliminary.
The 'header' is copied into the new file with some 
addition in the softwareList XML tag, 
hence a pymzml.run.Reader Object needs to be passed 
over to the write function.

Writing of indexed mzML files is not possible at the moment

Example:

>>> example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
>>> run  = pymzml.run.Reader(example_file, MS1_Precision = 5e-6)
>>> run2 = pymzml.run.Writer(filename = 'write_test.mzML', run= run , overwrite = True)
>>> specOfIntrest = run[2]
>>> run2.addSpec(spec)
>>> run2.save()


"""

from __future__ import print_function
import pymzml
import get_example_file

if __name__ == '__main__':  
    example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
    run  = pymzml.run.Reader(
        example_file,
        MS1_Precision = 5e-6
    )
    run2 = pymzml.run.Writer(
        filename = 'write_test.mzML',
        run= run,
        overwrite = True
    )
    spec = run[1]
    run2.addSpec(spec)
    run2.save()    
