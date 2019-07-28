#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pymzml
import get_example_file


def main():
    """
    Accessing positive or negative polarity of scan using obo 1.1.0

    usage:

        ./polarity.py

    """
    example_file = get_example_file.open_example("small.pwiz.1.1.mzML")
    run = pymzml.run.Reader(example_file, obo_version="1.1.0")
    for spec in run:
        negative_polarity = spec["negative scan"]
        if negative_polarity is None:
            negative_polarity = False
        if negative_polarity == "":
            negative_polarity = True
        positive_polarity = spec["positive scan"]
        if positive_polarity is None:
            positive_polarity = False
        if positive_polarity == "":
            positive_polarity = True
        else:
            positive_polarity = False
        print(
            "Polarity negative {0} - Polarity positive {1}".format(
                negative_polarity, positive_polarity
            )
        )
        exit(1)

    return


if __name__ == "__main__":
    main()
