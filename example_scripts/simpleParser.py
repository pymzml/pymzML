#!/usr/bin/env python3.4
import pymzml
import sys
run = pymzml.run.Reader(sys.argv[1])
# print( run[10000].keys() )
for n, spec in enumerate( run ):
    print('Spectrum {0}, MS level {ms level}'.format(
        n,
        **spec ),
        end = '\r')

print()
