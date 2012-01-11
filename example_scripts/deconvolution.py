#!/usr/bin/env python

"""

Example for retrieving monoisotopic peaks from the processed spectrm.
The python-matplotlib has to be installed for plotting. Otherwise a list of
monoisotopic peaks will be returned.

Example:

>>> import pymzml, get_example_file
>>> example_file = get_example_file.open_example('deconvolution.mzML.gz')
>>> run = pymzml.MSRun(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
>>> for spectrum in run:
...     if spectrum.lvl == 2:
...        l = spectrum.get_deisotopedMZ_for_chargeDeconvolution()
...         if len(l) > 0:
...             print(l)

"""

from __future__ import print_function
import sys
import os
import pymzml
import get_example_file

def deconvolution():
    example_file = get_example_file.open_example('deconvolution.mzML.gz')
    run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
    for spec in run:
        charge_dict = dict()
        for mz, i, charge, n in spec._get_deisotopedMZ_for_chargeDeconvolution():
            charge_dict[mz] = charge
        
        
        p   = pymzml.plot.Factory()
        
        tmp = spec.deRef()
        tmp.reduce((590, 615))
    
        p.newPlot(header = 'centroided I', mzRange = [590, 615])
        p.add(spec.centroidedPeaks, color=(200,00,00), style='sticks')
        for mz, i in tmp.centroidedPeaks:
            try:
                p.add([ (mz,'mz = {0}, z = {1}'.format(mz, charge_dict[mz]) ) ], color=(000,200,00), style='label' )
            except KeyError:
                p.add([ (mz,'mz = {0}'.format(mz) ) ], color=(000,200,00), style='label' )

        tmp = spec.deRef()
        tmp.reduce((1190, 1215))

        p.newPlot(header = 'centroided II', mzRange = [1190, 1215])
        p.add(spec.centroidedPeaks, color=(200,00,00), style='sticks')
        for mz, i in tmp.centroidedPeaks:
            try:
                p.add([ (mz,'mz = {0}, z = {1}'.format(mz, charge_dict[mz]) ) ], color=(000,200,00), style='label' )
            except KeyError:
                p.add([ (mz,'mz = {0}'.format(mz) ) ], color=(000,200,00), style='label' )        
        
        
        
        p.newPlot(header = 'deconvoluted', mzRange = [1190, 1215])
        p.add(spec.deconvolutedPeaks, color=(200,00,00), style='sticks')

        tmp = spec.deRef()
        tmp.reduce((1190, 1215))
        for mass, i in tmp.deconvolutedPeaks:
            p.add([ (mass,'mass = {0}'.format(mass) ) ], color=(000,200,00), style='label' )  
        
        p.save(filename = "output/deconvolution.xhtml",)
        
if __name__ == '__main__':
    deconvolution()
