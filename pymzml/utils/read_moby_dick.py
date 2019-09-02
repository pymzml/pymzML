#!/usr/bin/env python3

"""
Show chapter x of indexed gzipped moby dick


Usage:

    python read_moby_dick.py <Chapter>
"""

# Python mzML module - pymzml
# Copyright (C) 2010-2019 M. Kösters, C. Fufezan
#     The MIT License (MIT)

#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:

#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.

#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.

from GSGR import GSGR
import sys
import time

my_Reader = GSGR("./Moby_Dick_indexed.gz")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
    else:
        try:
            chap_num = int(sys.argv[1])
        except:
            chap_num = sys.argv[1]
        print(
            """
    Reading indexed gzip and retrieving chapter {0}
            """.format(
                chap_num
            )
        )
        s = time.time()
        print(
            """{0}

    Took {1:.5f} seconds to retrieve chapter

            """.format(
                my_Reader.read_block(chap_num), time.time() - s
            )
        )
