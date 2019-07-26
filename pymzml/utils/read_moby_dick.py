#!/usr/bin/env python3

"""
Show chapter x of indexed gzipped moby dick


Usage:

    python read_moby_dick.py <Chapter>
"""

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
