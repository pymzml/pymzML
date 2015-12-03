#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This function shows how to plot a simple spectrum. It can be directly
plotted via this script or using the python console

Example of plotting a spectrum:

>>> import pymzml, get_example_file
>>> mzMLFile = 'profile-mass-spectrum.mzml'
>>> get_example_file.open_example(mzMLFile)
>>> run = pymzml.run.Reader("mzML_example_files/"+mzMLFile, MSn_Precision = 25e-6)
>>> p = pymzml.plot.Factory()
>>> for spec in run:
>>>     p.newPlot()
>>>     p.add(spec.peaks, color=(200,0,0), style='circles')
>>>     p.add(spec.centroidedPeaks, color=(0,0,0), style='sticks')
>>>     p.add(spec.reprofiledPeaks, color=(0,255,0), style='circles')
>>>     p.save( filename="output/plotAspect.xhtml" , mzRange = [744.7,747] )

"""

from __future__ import print_function
import pymzml
import get_example_file

def main( file = None ):
    mzMLFile = 'profile-mass-spectrum.mzml'
    get_example_file.open_example(mzMLFile)
    run = pymzml.run.Reader("mzML_example_files/"+mzMLFile, MSn_Precision = 25e-6)
    p = pymzml.plot.Factory()
    for spec in run:
        p.newPlot()
        p.add(spec.peaks, color=(200,0,0), style='squares')
        p.add(spec.centroidedPeaks, color=(0,0,0), style='sticks')
        p.add(spec.reprofiledPeaks, color=(25,0,200), style='circles')
        p.save( filename="output/plotAspect.xhtml" , mzRange = [744.7,747] )

if __name__ == '__main__':
    main()
