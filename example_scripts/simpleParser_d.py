#!/usr/bin/env python3.2
import pymzml, sys
run = pymzml.run.Reader(sys.argv[1])
with open("pyOutput.txt","w") as io:
    for spec in run:
        for m,i in spec.peaks:
            io.write("{0}\t{1}\n".format(m,i))
