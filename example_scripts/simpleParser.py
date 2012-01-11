#!/usr/bin/env python3.2
import pymzml, sys
run = pymzml.run.Reader(sys.argv[1])
for spec in run:
    pass
