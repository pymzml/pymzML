#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pymzml


def main():
    """
    Compare multiple spectra and return the cosine distance between them.
    The returned value is between 0 and 1, a returned value of 1
    represents highest similarity.

    usage:

        ./compare_spectra.py

    """
    example_file = os.path.join(
        os.path.dirname(__file__), os.pardir, "tests", "data", "example.mzML"
    )
    print(
        """
            Comparing spectra
        """
    )
    # print(example_file)
    run = pymzml.run.Reader(example_file)
    tmp = []
    for spec in run:
        if spec.ms_level == 1:
            print("Parsing spectrum lvl 1 has id {0}".format(spec.ID))
            tmp.append(spec)
            if len(tmp) >= 3:
                break

    print("Print total number of specs collected {0}".format(len(tmp)))
    for compare_tuples in [(0, 1), (0, 2), (1, 2)]:
        print(
            "Cosine between spectra {0} & {1} is {2:1.4f}".format(
                compare_tuples[0] + 1,
                compare_tuples[1] + 1,
                tmp[compare_tuples[0]].similarity_to(tmp[compare_tuples[1]]),
            )
        )

    print(
        "Cosine score between first spectrum against itself: {0:1.4f}".format(
            tmp[0].similarity_to(tmp[0])
        )
    )


if __name__ == "__main__":
    main()
