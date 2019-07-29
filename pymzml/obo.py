# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Class to parse the obo file and set up the accessions library

The OBO parser has been designed to convert MS:xxxxx tags to their appropriate
names. A minimal set of MS accession is used in pymzML, but additional
accessions can easily be queried.

The obo translator is used internally to associate names with MS:xxxxxxx tags.

The OboTranslator Class generates a dictionary and several lookup tables.
e.g.

::

    >>> from pymzml.obo import OboTranslator as OT
    >>> translator = OT()
    >>> translator['MS:1000127']
    'centroid mass spectrum'
    >>> translator['positive scan']
    {'is_a': 'MS:1000465 ! scan polarity', 'id': 'MS:1000130', 'def':
    '"Polarity of the scan is positive." [PSI:MS]', 'name': 'positive scan'}
    >>> translator['scan']
    {'relationship': 'part_of MS:0000000 ! Proteomics Standards Initiative Mass
    Spectrometry Ontology', 'id': 'MS:1000441', 'def': '"Function or process of
    the mass spectrometer where it records a spectrum." [PSI:MS]', 'name':
    'scan'}
    >>> translator['unit']
    {'relationship': 'part_of MS:0000000 ! Proteomics Standards Initiative Mass
    Spectrometry Ontology', 'id': 'MS:1000460', 'def': '"Terms to describe
    units." [PSI:MS]', 'name': 'unit'}

pymzML comes with the queryOBO.py script that can be used to interrogate the
OBO file. Please refer to :ref:`example_scripts` for further usage information.

::

    $ ./example_scripts/queryOBO.py "scan time"
    MS:1000016
    scan time
    "The time taken for an acquisition by scanning analyzers." [PSI:MS]
    Is a: MS:1000503 ! scan attribute
    $


::

    $ ./example_scripts/queryOBO.py 1000016
    MS:1000016
    scan time
    "The time taken for an acquisition by scanning analyzers." [PSI:MS]
    MS:1000503 ! scan attribute
    $


"""

# pymzml
#
# Copyright (C) 2010-2016 M. Kösters, C. Fufezan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os
import re
import gzip


class OboTranslator(object):
    """
    Generates a mapping from MS:xxxxx to names and vice versa for a specific
    obo version

    Args:
        version (str): obo version
    """

    def __init__(self, version=None):
        self.version = self.__normalize_version(version)
        self.all_dicts = []
        self.id = {}
        self.name = {}
        self.definition = {}
        self.lookups = [self.id, self.name, self.definition]
        self.MS_tag_regex = re.compile(r"MS:[0-9]*")

        # Only parse the OBO when necessary, not upon object construction
        self.__obo_parsed = False

    def __setitem__(self, key, value):
        raise TypeError("OBO translator dictionaries only support assignment via .add")

    def __getitem__(self, key):
        if not self.__obo_parsed:
            self.parseOBO()

        for lookup in self.lookups:
            if key in lookup:
                if self.MS_tag_regex.match(key):
                    try:
                        return lookup[key]["name"]
                    except:
                        pass
                return lookup[key]
        return None

    @staticmethod
    def __normalize_version(version):
        """
        Ensure that a version has 3 components, defaulting to .0 for the
        missing components.

        Args:
            version (str): The original version to modify.

        Returns:
            version (str): The version, normalized to ensure that it has 3
                parts.
        """
        if version is not None:
            parts = version.split(".")

            missing_parts = 3 - len(parts)
            if missing_parts > 0:
                version = ".".join(parts + ["0"] * missing_parts)

        return version

    def parseOBO(self):
        self.__obo_parsed = True
        """
        Locate and parse the OBO file in the OBO root directory.

        Note:

           cx_Freeze friendly. If using cx_Freeze, place the OBO folder at
           the location of sys.executable.
        """

        # TODO: Try to get all the versions, even those without well-defined
        #       version numbers, or get remote hosting of all of the versions
        #       and only download one at will on demand.

        # Modify the root for cx_freeze
        if getattr(sys, "frozen", False):
            obo_root = os.path.dirname(sys.executable)
        else:
            obo_root = os.path.dirname(__file__)

        obo_file = os.path.join(
            obo_root,
            "obo",
            "psi-ms{0}.obo".format("-" + self.version if self.version else ""),
        )

        if os.path.exists(obo_file):
            pass
        elif os.path.exists(obo_file + ".gz"):
            obo_file = obo_file + ".gz"
        else:
            raise IOError("Could not find obo file {0}".format(obo_file))

        with open(obo_file, "rb") as fin:
            # never rely on file extensions!
            first_two_bytes = fin.read(2)
            # check if file is gzipped by magic bytes
            if first_two_bytes == b"\x1f\x8b":
                open_func = gzip.open
            else:
                raise Exception(
                    "Filename has .gz extension but is missing the gzip magic bytes.\n"
                    "The file may be corrupted or not gzipped."
                )

        with open_func(obo_file, "rt") as obo:
            collections = {}
            collect = False
            for line in obo:
                if line.strip() in ("[Term]", ""):
                    collect = True
                    if not collections:
                        continue
                    self.add(collections)
                    collections = {}
                else:
                    if line.strip() != "" and collect is True:
                        k = line.find(":")
                        collections[line[:k]] = line[k + 1 :].strip()
        return

    def add(self, collection_dict):
        """
        Add a new dict to the translator.

        Args:
            collection_dict (dict): python dict containing MS:xxxxxxx name
                mapping.
        """
        if not self.__obo_parsed:
            self.parseOBO()

        self.all_dicts.append(collection_dict)
        if "id" in collection_dict.keys():
            self.id[collection_dict["id"]] = self.all_dicts[-1]
        if "name" in collection_dict.keys():
            self.name[collection_dict["name"]] = self.all_dicts[-1]
        if "def" in collection_dict.keys():
            self.definition[collection_dict["def"]] = self.all_dicts[-1]

        return

    def checkOBO(self, idTag, name):
        """
        Check if idTag equals name in currently used obo version.

        Args:
            idTag (str): MS accession tag
            name  (str): trivial name of the accession

        Returns:
            boolean: True if idTag and name correspond, else False.
        """
        if not self.__obo_parsed:
            self.parseOBO()

        if self.id[idTag]["name"] == name:
            return True
        else:
            return False


if __name__ == "__main__":
    print(__doc__)
