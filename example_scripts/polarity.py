#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Accessing positive or negative polarity of scan using obo 1.1.0

"""

from __future__ import print_function
import pymzml
import get_example_file

def main(verbose = False):
    example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
    run = pymzml.run.Reader(
        example_file,
        MSn_Precision = 250e-6,
        obo_version = '1.1.0',
        extraAccessions = [
            ('MS:1000129',['value']),
            ('MS:1000130',['value'])
        ]
    )
    for spec in run:
        negative_polarity = spec.get('MS:1000129', False)
        if negative_polarity == '':
            negative_polarity = True
        positive_polarity = spec.get('MS:1000130', False)
        if positive_polarity == '':
            positive_polarity = True
        print(
            'Polarity negative {0} - Polarity positive {1}'.format(
                negative_polarity,
                positive_polarity
            )
        )
        exit(1)

    return True

if __name__ == '__main__':
    main(verbose = True)
