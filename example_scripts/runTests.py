#!/usr/bin/env python3.2

"""
Testscript to demonstrate

"""
    
from __future__ import print_function
import highestPeaks
import parseAllExampleFiles
import hasPeak
import find_abundant_precursors
import compareSpectra
import chromatogram
import accessAllData
import searchScan

def main():
    
    print(highestPeaks.main(), 'highestPeaks.py')
    print(parseAllExampleFiles.main(), 'parseAllExampleFiles.py')
    print(hasPeak.main(), 'hasPeak.py')
    print(accessAllData.main(), 'accessAllData.py')
    print(find_abundant_precursors.main(), 'find_abundant_precursors.py')
    print(compareSpectra.main(), 'compareSpectra.py')
    print(chromatogram.main(), 'chromatogram.py')
    print(searchScan.main(), 'searchScan.py')
    
    


if __name__ == '__main__':
    main()
