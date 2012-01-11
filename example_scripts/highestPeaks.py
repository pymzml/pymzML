#!/usr/bin/env python3.2

"""
Testscript to isolate the n-highest peaks from an example file.

Example:

>>> example_file = get_example_file.open_example('deconvolution.mzML.gz')
>>> run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
>>> for spectrum in run:
...     if spectrum["ms level"] == 2:
...         if spectrum["id"] == 1770:
...             for mz,i  in spectrum.highestPeaks(5):
...                 print(mz,i)

"""
    
import sys
import pymzml
import get_example_file

def main(verbose = False):
    
    ref_intensities = set([9258.819334518503, 19141.735187697403, 20922.463809964283, 10594.642802391083, 9193.546071711491])
    
    example_file = get_example_file.open_example('deconvolution.mzML.gz')
    
    run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
    
    highest_i_list = list()
    
    for spectrum in run:
        if spectrum["ms level"] == 2:
            if spectrum["id"] == 1770:
                for mz,i  in spectrum.highestPeaks(5):
                    highest_i_list.append(i)

    if set(highest_i_list) == set(ref_intensities):
        if verbose:
            print("Function .highestPeaks worked properly")
        return True
    else:
        return False


if __name__ == '__main__':
    main(verbose = True)
