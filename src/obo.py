#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
Class to parse the obo file and set up the accessions library

The OBO parse has been designed to convert MS:xxxxx tags to their appropriate 
names. A minimal set of MS acession is used in pymzml, but additional accessions
can easily added, using the extraAccession parameter during 
:py:class:`run.Reader` initialization.

The obo translator is used internally to associate names with MS:xxxxxxx tags.

The oboTranslator Class generates a dictionary and several lookup tables.
e.g.

::

    >>> from pymzml.obo import oboTranslator as OT
    >>> translator = OT()
    >>> len(translator.id.keys()) # Numer of parsed entries
    737
    >>> translator['MS:1000127']
    'centroid mass spectrum'
    >>> translator['positive scan']
    {'is_a': 'MS:1000465 ! scan polarity', 'id': 'MS:1000130', 'def': '"Polarity 
    of the scan is positive." [PSI:MS]', 'name': 'positive scan'}
    >>> translator['scan']
    {'relationship': 'part_of MS:0000000 ! Proteomics Standards Initiative Mass 
    Spectrometry Ontology', 'id': 'MS:1000441', 'def': '"Function or process of 
    the mass spectrometer where it records a spectrum." [PSI:MS]', 'name': 
    'scan'}
    >>> translator['unit']
    {'relationship': 'part_of MS:0000000 ! Proteomics Standards Initiative Mass 
    Spectrometry Ontology', 'id': 'MS:1000460', 'def': '"Terms to describe 
    units." [PSI:MS]', 'name': 'unit'}

pymzML comes with the queryOBO.py script that can be used to interogate the OBO 
file.

::

    $ ./example_scripts/queryOBO.py "scan time"
    MS:1000016
    scan time
    "The time taken for an acquisition by scanning analyzers." [PSI:MS]
    Is a: MS:1000503 ! scan attribute
    $ 
"""


# pymzml
#
# Copyright (C) 2010-2011 T. Bald, J. Barth, M. Specht, C. Fufezan 
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


from __future__ import print_function
import sys
import os
import pymzml

class oboTranslator(object):
    def __init__(self, version='1.1.0'):
        self.version = version
        self.allDicts = []
        
        self.id = {}
        self.name = {}
        self.definition = {}
        self.lookups = [ self.id, self.name, self.definition ]  # replace_by could be another one ...
        
        self.parseOBO()
        
    def __setitem__(self,key,value):
        return
        
    def __getitem__(self,key):
        for lookup in self.lookups:
            if key in lookup.keys():
                if key[:2] == 'MS':
                    try:
                        return lookup[key]['name']
                    except:
                        pass
                return lookup[key]
        return 'None'
        
    def parseOBO(self):
        """
        Parse the obo file in folder obo/
        (would be great to have all versions. Must convience PSI to add version number at the file .. :))
        """
        oboFile = os.path.normpath('{0}/obo/psi-ms-{1}.obo'.format(os.path.dirname(pymzml.obo.__file__),self.version))
        if os.path.exists(oboFile):
            with open(oboFile) as obo:
                collections = {}
                collect = False
                for line in obo:
                    if line.strip() == '[Term]':
                        self.add(collections)
                        collect = True
                        collections = {}
                    else:
                        if line.strip() != '' and collect == True:
                            k = line.find(":")
                            collections[line[:k]] = line[k+1:].strip()
        else:
            print("No obo file version {0} (psi-ms-{0}.obo) found.".format(self.version), file=sys.stderr)
            exit(1)
        return

    def add(self,collection_dict):
        self.allDicts.append(collection_dict)
        if 'id' in collection_dict.keys():
            self.id[collection_dict['id']] = self.allDicts[len(self.allDicts)-1]
        if 'name' in collection_dict.keys():
            self.name[collection_dict['name']] = self.allDicts[len(self.allDicts)-1]
        if 'def' in collection_dict.keys():
            self.definition[collection_dict['def']] = self.allDicts[len(self.allDicts)-1]
        else:
            pass
        return
        
    def checkOBO(self,idTag,name):
        if self.id[idTag]['name'] == name:
            return True
        else:
            return False
    
if __name__ == '__main__':
    print(__doc__)
