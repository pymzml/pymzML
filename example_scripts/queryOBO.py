#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
from collections import defaultdict

import pymzml.obo


FIELDNAMES = ["id", "name", "def", "is_a"]


def main(args):
    """
    Use this script to interrogate the OBO database files.

    usage:

        ./queryOBO.py [-h] [-v VERSION] query

    Example::

      $ ./queryOBO.py'scan time'
      MS:1000016
      scan time
      'The time taken for an acquisition by scanning analyzers.' [PSI:MS]
      Is a: MS:1000503 ! scan attribute

    Example::

        $ ./queryOBO.py 1000016
        MS:1000016
        scan time
        "The time taken for an acquisition by scanning analyzers." [PSI:MS]
        MS:1000503 ! scan attribute


    """
    obo = pymzml.obo.OboTranslator(version=args.version)
    obo.parseOBO()
    if args.query.isdigit():
        print(search_by_id(obo, args.query))
    else:
        for ix, match in enumerate(search_by_name(obo, args.query)):
            print("#{0}".format(ix))

            for fieldname in ("id", "name", "def"):
                print(match[fieldname])

            if "is_a" in match:
                print("Is a:", match["is_a"])


def search_by_name(obo, name):
    print("Searching for {0}".format(name.lower()))
    matches = []
    for lookup in obo.lookups:
        for key in lookup.keys():
            if name.lower() in key.lower():
                match = defaultdict(str)

                for fieldname in FIELDNAMES:
                    if fieldname in lookup[key].keys():
                        match[fieldname] = lookup[key][fieldname]

                matches.append(match)

    return matches


def search_by_id(obo, id):
    key = "MS:{0}".format(id)
    return_value = ""
    for lookup in obo.lookups:
        if key in lookup:
            if obo.MS_tag_regex.match(key):
                for fn in FIELDNAMES:
                    if fn in lookup[key].keys():
                        return_value += "{0}\n".format(lookup[key][fn])
    return return_value


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(usage=__doc__)
    argparser.add_argument(
        "query", help="an accession or part of an OBO term name to look for"
    )
    argparser.add_argument(
        "-v",
        "--version",
        default="1.1.0",
        help="""
            the version of the OBO to use; valid options are 1.0.0, 1.1.0, and 1.2,
            default is 1.1.0
        """,
    )

    args = argparser.parse_args()

    main(args)
