#!/usr/bin/env python3.2

"""
Testscript to demonstrate functionality of function :py:func:`spec.Spectrum.hasPeak` 
or :py:func:`spec.Spectrum.hasDeconvolutedPeak`

Example:

>>> import pymzml, get_example_file
>>> example_file = get_example_file.open_example('deconvolution.mzml.gz')
>>> run = pymzml.run.run(example_file, precisionms1 = 5e-6, precisionmsn = 20e-6)
>>> for spectrum in run:
...     if spectrum["ms level"] == 2:
...             peak_to_find = spectrum.haspeak(1016.5404)
...             print(peak_to_find)
(1016.5404, 19141.735187697403)

"""

from __future__ import print_function
import sys
import pymzml
import get_example_file

def main(verbose = False):
    example_file = get_example_file.open_example('deconvolution.mzML.gz')
    run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
    for spectrum in run:
        if verbose:
            print("Processing spectrum #{0}".format(spectrum['id']), end="\r")
            print('')
        if spectrum['ms level'] == 2:
            test1 = spectrum.hasDeconvolutedPeak(1044.559675129575)
            test2 = spectrum.hasDeconvolutedPeak(1044.5804)
            test3 = spectrum.hasDeconvolutedPeak(1044.5806)
            test4 = spectrum.hasDeconvolutedPeak(1044.5800)
            test5 = spectrum.hasDeconvolutedPeak(6000)
            test6 = spectrum.hasPeak(1016.5402567492666)
            test7 = spectrum.hasPeak(6000)

            tests = [False, False, False, False, False, False, False]
            if test1 == [(1044.559675129575, 3809.4356300564586)]:
                tests[0] = True
            if test2 == [(1044.559675129575, 3809.4356300564586)]:
                tests[1] = True
            if test3 == []:
                tests[2] = True
            if test4 == [(1044.559675129575, 3809.4356300564586)]:
                tests[3] = True
            if test5 == []:
                tests[4] = True
            if test6 == [(1016.5402567492666, 19141.735187697403)]:
                tests[5] = True
            if test7 == []:
                tests[6] = True
            
            all = True
            for i in range(len(tests)):
                if not tests[i]:
                    all = False
            
            if all:
                if verbose:
                    print('All tests were successful.')
            else:
                print(tests)
                
                
                
                
            if verbose:
                print('deconvoluted peaks list:')
                print('')
                print('centroided peaks list:')
                print(spectrum.centroidedPeaks)
                print('')
                print('deconvolutedPeaks list:')
                print(spectrum.deconvolutedPeaks)
                print('')
                print("1044.559675129575 in deconvoluted spectrum? (should be)", test1)
                print("1044.559675129575 + 20 ppm = 1044.5804 in deconvoluted spectrum? (should be)", test2)
                print("1044.559675129575 + >20 ppm = 1044.5806 in deconvoluted spectrum? (shouldn't)", test3)
                print("1044.5800 in deconvoluted spectrum? (should be)", test4)
                print("6000 in deconvoluted spectrum (shouldn't)?", test5)
                print("1016.5402567492666 in centroided peaks (True)", test6)
                print("6000 in centroided peaks (None)", test7)
                
            if all:
                return True

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == '-v':
            main(True)
    else:
        main()
