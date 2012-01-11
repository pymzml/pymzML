#!/usr/bin/env python3.2

"""
Testscript to demonstrate an easy isoloation of the most abundant, isolated 
precusors for MSn spectra.Thus exclusion list for further MS runs can be 
generated. In this example all precursors which were isolated more than 5 
times are found and printed.

Example:

>>> import pymzml, get_example_file, operator.item
>>> import collections import defaultdict as ddict
>>> from operator import itemgetter
>>> example_file = get_example_file.open_example('dta_example.mzML')
>>> run = pymzml.run.Reader(example_file , MS1_Precision = 5e-6 , MSn_Precision = 20e-6 )
>>> precursor_count_dict = ddict(int)
>>> for spectrum in run:
>>>    if spectrum["ms level"] == 2:
>>>        if "precursors" in spectrum.keys():
>>>            precursor_count_dict[round(float(spectrum["precursors"][0]["mz"]),3)] += 1
>>> for precursor, frequency in sorted(precursor_count_dict.items()):
>>>     print("{0}\\t{1}".format(precursor, frequency))
"""
    
import sys
import pymzml
from collections import defaultdict as ddict
from operator import itemgetter
import get_example_file

def main():
    
    ref = set([(801.266,1),(419.115,1),(460.227,1),(723.888,1),(948.349,1),(406.261,1),(919.143,1),(536.459, 1),(1082.504,1),(474.342, 1)])

    
    example_file = get_example_file.open_example('dta_example.mzML')
    
    run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
    precursor_count_dict = ddict(int)
    for spectrum in run:
        if spectrum["ms level"] == 2:
            if "precursors" in spectrum.keys():
                precursor_count_dict[round(float(spectrum["precursors"][0]["mz"]),3)] += 1

    precursor_set = set()
    for precursor, frequency in sorted(precursor_count_dict.items(), key = itemgetter(1)):
        precursor_set.add((precursor, frequency))
    if precursor_set == ref:
        return True
    else:
        return False
if __name__ == '__main__':
    main()
