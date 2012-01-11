#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This function shows how to plot a simple spectrum. It can be directly
plotted via this script or using the python console

Example of plotting a spectrum:

>>> import pymzml, get_example_file
>>> mzMLFile = 'profile-mass-spectrum.mzml'
>>> example_file = get_example_file.open_example(mzMLFile)
>>> run = pymzml.run.Reader("../mzML_example_files/"+mzMLFile, MSn_Precision = 250e-6)
>>> p = pymzml.plot.Factory()
>>> for spec in run:
>>>     p.newPlot()
>>>     p.add(spec.peaks, color=(200,00,00), style='circles')
>>>     p.add(spec.centroidedPeaks, color=(00,00,00), style='sticks')
>>>     p.add(spec.reprofiledPeaks, color=(00,255,00), style='circles')
>>>     p.save( filename="output/plotAspect.xhtml" , mzRange = [744.7,747] )

"""

from __future__ import print_function
import sys

import pymzml
import get_example_file

def main():

    
    mzMLFile = 'profile-mass-spectrum.mzml'
    example_file = get_example_file.open_example(mzMLFile)
    
    run = pymzml.run.Reader(example_file, MSn_Precision = 250e-6)
    p   = pymzml.plot.Factory()
    
    for spec in run:
        p.newPlot()
        p.add(spec.peaks, color=(200,00,00), style='circles')
        p.add(spec.centroidedPeaks, color=(00,00,00), style='sticks')
        p.add(spec.reprofiledPeaks, color=(00,255,00), style='circles')
        p.save( filename="output/plotAspect.xhtml" , mzRange = [744.7,747] )
        break
    return
    
if __name__ == '__main__':  
    main()
