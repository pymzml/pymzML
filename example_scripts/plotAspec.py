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

def main( file = None):

    if file == None:
        mzMLFile = 'profile-mass-spectrum.mzml'
        example_file = get_example_file.open_example(mzMLFile)
    else:
        example_file = file

    run = pymzml.run.Reader(example_file, MSn_Precision = 250e-6)
    p   = pymzml.plot.Factory()
    specs = [ 4927,4930,4934,4936,4938,4942,4946,4948,4950,4954,4955,4957,4959,4962,4965,4967,4971,4976,4979,4982,4985,4990,4991,4995,4999,5004]


    for specID in specs:
        spec = run[ specID ]
        p.newPlot()
        # p.add(spec.peaks, color=(200,00,00), style='circles')
        p.add(spec.reprofiledPeaks, color=(100,100,100), style='triangle')
        p.add(spec.centroidedPeaks, color=(00,00,00), style='sticks')
        # break
    p.save( filename="output/plotAspect.xhtml" , mzRange = [840.,853.] )
    return

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        main( file = sys.argv[1] )