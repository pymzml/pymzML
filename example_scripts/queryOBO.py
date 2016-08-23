#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''%(prog)s [-h] [-v VERSION] query

Use this script to interrogate the OBO database files.

example:
  $ %(prog)s 'scan time'
  MS:1000016
  scan time
  'The time taken for an acquisition by scanning analyzers.' [PSI:MS]
  Is a: MS:1000503 ! scan attribute
'''

from __future__ import print_function

from collections import defaultdict
import argparse

import pymzml.obo


def search_by_name(obo, name):
    print('Searching for {0]'.format(name.lower()))
    matches = []
    for lookup in obo.lookups:
        for key in lookup.keys():
            if name.lower() in key.lower():
                match = defaultdict(str)

                for fieldname in ('id', 'name', 'def', 'is_a'):
                    if fieldname in lookup[key].keys():
                        match[fieldname] = lookup[key][fieldname]

                matches.append(match)

    return matches


def search_by_id(obo, id):
    return obo['MS:{0}'.format(id)]


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        usage=__doc__,
    )
    argparser.add_argument('query', help='an accession or part of an OBO term name to look for')
    argparser.add_argument(
        '-v', '--version', default='1.1.0',
        help='''
            the version of the OBO to use; valid options are 1.0.0, 1.1.0, and 1.2,
            default is 1.1.0
        ''',
    )

    args = argparser.parse_args()

    obo = pymzml.obo.oboTranslator(version=args.version)

    if args.query.isdigit():
        print(search_by_id(obo, args.query))
    else:
        for ix, match in enumerate(search_by_name(obo, args.query)):
            print('#{0}'.format(ix))

            for fieldname in ('id', 'name', 'def'):
                print(match[fieldname])

            if 'is_a' in match:
                print('Is a:', match['is_a'])
