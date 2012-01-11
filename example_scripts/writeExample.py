#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test of the mzML writing functionality.

This is very priliminary. 
The 'header' is copied into the new file with some 
addition in the softwareList XML tag, 
hence a pymzml.run.Reader Object needs to be passed 
over to the write function.

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

if __name__ == '__main__':  
    run  = pymzml.run.Reader('../mzML_example_files/100729_t300_100729172744.mzML', MS1_Precision = 5e-6)
    run2 = pymzml.run.Writer(filename = 'write_test.mzML', run= run , overwrite = True)
    spec = run[1000]
    run2.addSpec(spec)
    run2.save()    
