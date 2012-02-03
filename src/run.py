#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
The class :py:class:`Reader` has been designed to selectivly extract data
from a mzML file and to expose the data as a python object.
Necessary information are read in and stored in a fast
accesible format.
The reader itself is an iterator, thus looping over all spectra
follows the classical pythonian syntax.
Additionally one can random access spectra by their nativeID
if the file if not compressed or truncated by a conversion Program.

The class :py:class:`Writer` is still in development.

"""

# pymzml
#
# Copyright (C) 2010-2011 T. Bald, J. Barth, A. Niehues, M. Specht, C. Fufezan
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
import re
import os
import bisect

from xml.etree import cElementTree

from collections import defaultdict as ddict

import pymzml.spec

import pymzml.obo
import pymzml.minimum



class Reader(object):
    """
    .. function:: __init__(path*  [,noiseThreshold = 0.0, extraAccessions = None, MS1_Precision = 5e-6, MSn_Precision = 20e-6])

    Initializes an mzML run and returns an iterator.

    :param path: path to mzML file. File can be gzipped.
    :type path: string

    :param extraAccessions: list of additional (accession,fieldName) tuples.


        For example, ('MS:1000285',['value']) will extract the "total ion
        current" and store it under two keys in the spectrum, i.e.
        spectrum["total ion current"] or spectrum['MS:1000285'].

        The translated name is extracted from the current OBO file,
        hence the name that is defined by the HUPO-PSI consortium is used. (http://www.psidev.info/).

        pymzML comes with an example script queryOBO.py which can be used to lookup
        the names or MS tags (see: :py:obj:`queryOBO`).

        The value, i.e. which xml property has to be extraced has to be provided by the user.
        Multiple values can be used as input, i.e. ( 'MS:1000016' , ['value','unitName'] ) will extract scan time and its unit.

    :type extraAccessions: list of tuples
    :param MS1_Precision: measured precision of MS1 spectra
    :type MS1_Precision: float
    :param MSn_Precision: measured precision of MSn spectra
    :type MSn_Precision: float

    Example:

    >>> run = pymzml.run.Reader("../mzML_example_files/100729_t300_100729172744.mzML.gz" ,
                            MS1_Precision = 20e-6 )
    """

    def __init__(
                     self,
                     path,
                     noiseThreshold = 0.0,
                     extraAccessions = None,
                     MS1_Precision = 5e-6,
                     MSn_Precision = 20e-6
        ):


        # self.param contains user-specified parsing parameters
        self.param = dict()

        self.param['noiseThreshold'] = noiseThreshold
        self.param['MS1_Precision'] = MS1_Precision
        self.param['MSn_Precision'] = MSn_Precision
        self.param['accessions'] = { }

        # self.info contains information extracted from the mzML file
        self.info = dict()
        self.info['offsets'] = ddict()
        self.info['filename'] = path
        self.info['offsetList'] = []

        self.MS1_Precision = MS1_Precision

        self.elementList = []

        # Default stuff
        #self.spectrum = pymzml.spec.Spectrum(measuredPrecision = MS1_Precision)
        #self.spectrum.clear()
        self.spectrum       = pymzml.spec.Spectrum(measuredPrecision = MS1_Precision , param = self.param)
        self.spectrum.clear()
        #

        if self.info['filename'].endswith('.gz'):
            import gzip, codecs
            self.info['fileObject'] = codecs.getreader("utf-8")(gzip.open(self.info['filename']))
            self.info['seekable'] = False
        else:
            self.info['fileObject'] = open(self.info['filename'],'r')
            self.info['seekable'] = True

            ### declare the seeker
            # read encoding ... maybe not really needed ...
            self.seeker = open(self.info['filename'],'rb')
            header = self.seeker.readline()
            encodingPattern = re.compile( b'encoding="(?P<encoding>[A-Za-z0-9-]*)"')
            match = encodingPattern.search(header)
            if match:
                self.info['encoding'] = bytes.decode( match.group('encoding'))
            else:
                self.info['encoding'] = None

            #reading last 1024 bytes to find chromatogram Pos and SpectrumIndex Pos
            indexListOffsetPattern = re.compile( b'<indexListOffset>(?P<indexListOffset>[0-9]*)</indexListOffset>' )
            chromatogramOffsetPattern = re.compile( b'(?P<WTF>[nativeID|idRef])="TIC">(?P<offset>[0-9]*)</offset' )
            self.info['offsets']['indexList'] = None
            self.info['offsets']['TIC'] = None
            self.seeker.seek(0,2)
            for _ in range(10): # max 10kbyte
                self.seeker.seek( -1024*_, 1 )
                for line in self.seeker:
                    match = chromatogramOffsetPattern.search(line)
                    #print(_, line)
                    if match:
                        self.info['offsets']['TIC'] = int(bytes.decode( match.group('offset')))
                    match = indexListOffsetPattern.search(line)
                    if match:
                        self.info['offsets']['indexList'] = int(bytes.decode( match.group('indexListOffset')))
                        #break
                if self.info['offsets']['indexList'] != None and self.info['offsets']['TIC'] != None:
                    break
            if self.info['offsets']['indexList'] == None:
                # fall back to non-seekable
                self.info['seekable'] = False
                # print('Could not find indexList. Falling back to non seekable.', file = sys.stderr)
            elif self.info['offsets']['TIC']  > os.path.getsize(self.info['filename']):
                self.info['seekable'] = False
                #print('mzML file was truncated, but offsets were not recalculated. Falling back to non seekable.', file = sys.stderr)
            else:
                # Jumping to index list and slurpin all specOffsets
                self.seeker.seek(self.info['offsets']['indexList'],0)
                spectrumIndexPattern = re.compile( b'(?P<type>[scan=|nativeID="])(?P<nativeID>[0-9]*)">(?P<offset>[0-9]*)</offset>' )
                simIndexPattern = re.compile( b'(?P<type>idRef=")(?P<nativeID>.*)">(?P<offset>[0-9]*)</offset>' )
                ## NOTE: this might be again different in another mzML versions!!
                ## 1.1 >> small_zlib.pwiz.1.1.mzML:     <offset idRef="controllerType=0 controllerNumber=1 scan=1">4363</offset>
                ## 1.0 >>                               <offset idRef="S16004" nativeID="16004">236442042</offset>
                ##  <offset idRef="SIM SIC 651.5">330223452</offset>\n'
                for line in self.seeker:
                    match_spec = spectrumIndexPattern.search(line)
                    if match_spec and match_spec.group('nativeID') == b'':
                        match_spec = None
                    match_sim  = simIndexPattern.search(line)
                    if match_spec:
                        self.info['offsets'][ int(bytes.decode( match_spec.group('nativeID'))) ] = int(bytes.decode( match_spec.group('offset')))
                        self.info['offsetList'].append(int(bytes.decode( match_spec.group('offset'))))
                    elif match_sim:
                        self.info['offsets'][ bytes.decode( match_sim.group('nativeID')) ] = int(bytes.decode( match_sim.group('offset')))
                        self.info['offsetList'].append(int(bytes.decode( match_sim.group('offset'))))
                # opening seeker in normal mode again
                self.seeker.close()
                self.seeker = open(self.info['filename'],'r')

        ### declare the iter
        self.iter = iter(cElementTree.iterparse(self.info['fileObject'], events = ( b'start',b'end'))) # NOTE: end might be sufficient

        # Move iter to spectrumList / chromatogramList
        while True:
            event, element = next(self.iter)
            if element.tag.endswith('}mzML'):
                if 'version' in element.attrib and len(element.attrib['version']) > 0:
                    self.info['mzmlVersion'] = element.attrib['version']
                else:
                    s = element.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation']
                    self.info['mzmlVersion'] = re.search( r'[0-9]*\.[0-9]*\.[0-9]*',   s  ).group()
            elif element.tag.endswith('}spectrumList'):
                break
            elif element.tag.endswith('}chromatogramList'):
                ## SRM only ?
                break
            else:
                pass

        ## parse obo, check MS tags and if they are ok in minimum.py (minimum required) ...
        self.OT = pymzml.obo.oboTranslator()

        for minimumMS, ListOfvaluesToExtract in pymzml.minimum.MIN_REQ:
            self.param['accessions'][minimumMS] = {
                                                    'valuesToExtract'   : ListOfvaluesToExtract ,
                                                    'name'              : self.OT[minimumMS] ,
                                                    'values'            : []
            }

        # parse extra accessions ...
        if extraAccessions != None:
            for accession, fieldIdentifiers in extraAccessions:
                if accession not in self.param['accessions'].keys():
                    self.param['accessions'][accession] = {
                                                        'valuesToExtract'   : [] ,
                                                        'name'              : self.OT[accession],
                                                        'values'            : []
                }
                for valueToExtract in fieldIdentifiers:
                    if valueToExtract not in self.param['accessions'][accession]['valuesToExtract']:
                        self.param['accessions'][accession]['valuesToExtract'].append(valueToExtract)

        return

    def __iter__(self):
        return self

    def __next__(self):
        """ The python 2.6+ iterator """
        return self.next()

    def next(self):
        """
        Iterator in class :py:class:`Run`:

        will return an instance of :py:class:`spec.Spectrum`, stored in run.spectrum.


        Example:

        >>> for spectrum in run:
        ...     print(spectrum['id'], end='\\r')

        """
        while True:
            event, element = next(self.iter, ('END','END'))
            # error? check cElementTree; conversion of data to 32bit-float mzml files might help
            # stop iteration when parsing is done
            if event == 'END':
                raise StopIteration
            if (element.tag.endswith('}spectrum') or element.tag.endswith('}chromatogram') ) and event == b'end':
                self.spectrum.initFromTreeObject(element)
                try:
                    self.elementList[-1].clear()
                except:
                    pass
                self.elementList.append(element)
                return self.spectrum

    def __getitem__(self,value):
        '''
        Random access to spectra if mzML fill is indexed,
        not compressed and not truncted.

        Example:

        >>> spectrum_with_nativeID_100 = msrun[100]

        '''
        answer = None
        if self.info['seekable'] == True:
            if len(self.info['offsets'].keys()) == 0:
                print("File does support random access, unfortunately indexlist missing, i.e. type not implemented yet ...", file=sys.stderr)

            if value in self.info['offsets']:
                startPos = self.info['offsets'][value]
                endPos_index = bisect.bisect_right(self.info['offsetList'],self.info['offsets'][value])
                if endPos_index == len(self.info['offsetList']):
                    endPos = os.path.getsize(self.info['filename'])
                else:
                    endPos = self.info['offsetList'][endPos_index]


                self.seeker.seek(startPos,0)
                data = self.seeker.read(endPos-self.info['offsets'][value])
                try:
                    self.spectrum.initFromTreeObject( cElementTree.fromstring( data ))
                except:
                    ## have closing </mzml> & </run> &or </spectrumList>
                    startingTag = data.split()[0]
                    stopIndex = data.index( '</'+startingTag[1:]+'>')
                    self.spectrum.initFromTreeObject( cElementTree.fromstring( data[:stopIndex+len(startingTag)+2] ))
                answer = self.spectrum
            else:
                print("Run does not contain spec with native ID {0}".format(value),file=sys.stderr)
                #print(self.info['offsets'].keys())

        else:
            self.iter = iter(cElementTree.iterparse(self.info['filename'], events = ( b'start',b'end'))) # NOTE: end might be sufficient

            for _ in self:
                if _['id'] == value:
                    answer = _
                    break
        return answer

class Writer(object):
    """
    .. function:: __init__(filename* ,run* [, overwrite = boolean])

    Initializes an mzML writer (beta stage).

    :param path: filename for the new mzML file.
    :type path: string
    :param run: Currently a pymzml.run.Reader object is required since we do not write the header by ourselves, yet.
    :type run: pymzml.run.Reader
    :param overwrite: force the re-initialization of mzML file, even if file exists.
    :type overwrite: boolean

    Example:

    >>> run = pymzml.run.Reader('../mzML_example_files/100729_t300_100729172744.mzML', MS1_Precision = 5e-6)
    >>> run2 = pymzml.run.Writer(filename = 'write_test.mzML', run= run , overwrite = True)
    >>> spec = run[1000]
    >>> run2.addSpec(spec)
    >>> run2.save()

    """
    def __init__(self,filename = None, run = None, overwrite = False):
        cElementTree.register_namespace("","http://psi.hupo.org/schema_revision/mzML_1.0.0")
        self.filename = filename
        self.lookup = {
        }

        self.newTree = None
        self.TreeBuilder = cElementTree.TreeBuilder()
        self.run = run
        self.info = {'counters': ddict(int) }
        if self.run.info['filename'].endswith('.gz'):
            import gzip, codecs
            io = codecs.getreader("utf-8")(gzip.open(self.run.info['filename']))
        else:
            io = open(self.run.info['filename'],'r')

        for event,element in cElementTree.iterparse(io, events = ( b'start',b'end')):
            if self.newTree == None:
                self.newTree = cElementTree.Element(element.tag,element.attrib)
            else:
                if event == b'start':
                    self.TreeBuilder.start(element.tag, element.attrib)
                    if element.tag.endswith('}run'):
                        self.lookup['run'] = cElementTree.Element(element.tag,element.attrib)
                    if element.tag.endswith('}spectrumList'):
                        self.lookup['spectrumList']     = cElementTree.Element(element.tag,element.attrib)
                        self.lookup['spectrumIndeces']  = cElementTree.Element('index',{'name':'spectrum'}),
                        break
                    elif element.tag.endswith('}chromatogramList'):
                        break
                    else:
                        pass
                else:
                    if element.tag.endswith('}softwareList'):
                        ### Insert pymzML software tag
                        ## Example :software id="pwiz_Reader_Thermo"><softwareParam accession="MS:1000615" cvRef="MS" name="ProteoWizard" version="1.0" />
                        self.TreeBuilder.start('software', {'id':'pymzML 0.7.1'})
                        self.TreeBuilder.start('softwareParam', {'accession':'MS:0000000', 'cvRef':'MS', 'name':'pymzML writer', 'version':'0.7.1'})
                        self.newTree.append(self.TreeBuilder.end('softwareParam'))
                        self.newTree.append(self.TreeBuilder.end('software'))
                    self.TreeBuilder.data(element.text)
                    self.newTree.append(self.TreeBuilder.end(element.tag))
        return

    def addSpec(self,spec):
        self._addTree(spec,typeOfSpec='spectrum')
        return

    def addChromatogram(self,spec):
        self._addTree(spec,typeOfSpec='chromatogram')
        return

    def _addTree(self,spec,typeOfSpec=None):
        if typeOfSpec not in self.lookup.keys():
            self.lookup['{0}List'.format(typeOfSpec)]     = cElementTree.Element('{0}List'.format(typeOfSpec) , {'count':0})
            self.lookup['{0}Indeces'.format(typeOfSpec)]  = cElementTree.Element('index',{'name':typeOfSpec})

        self.lookup[typeOfSpec+'List'].append( spec._xmlTree )
        offset = cElementTree.Element('offset')
        offset.text = 'Not implemented yet'
        offset.attrib = {'idRef': 'NaN', 'nativeID': str(spec['id'])}
        self.lookup[typeOfSpec+'Indeces'].append(offset)

        self.info['counters'][typeOfSpec] += 1

        return

    def save(self):
        for typeOfSpec in ['spectrum','chromatogram']:
            if typeOfSpec+'List' in self.lookup.keys():
                self.lookup['{0}List'.format(typeOfSpec)].set('count', str(self.info['counters'][typeOfSpec]))
                self.lookup['run'].append(self.lookup[typeOfSpec+'List'])
        self.newTree.append(self.lookup['run'])

        IndexList = cElementTree.Element('IndexList' , {'count': str(len(self.info['counters'].keys()))})

        for typeOfSpec in ['spectrum','chromatogram']:
            if typeOfSpec+'Indeces' in self.lookup.keys():
                IndexList.append(self.lookup['{0}Indeces'.format(typeOfSpec)])
        self.newTree.append(IndexList)


        self.prettyXMLformater(self.newTree)
        self.xmlTree = cElementTree.ElementTree(self.newTree)
        self.xmlTree.write(self.filename, encoding="ISO-8859-1", xml_declaration=True )
        return

    def prettyXMLformater(self, element, level = 0):
        # Modified version from
        # http://infix.se/2007/02/06/gentlemen-indent-your-xml
        # which is a modified version of
        # http://effbot.org/zone/element-lib.htm#prettyprint

        i = '\n{0}'.format(level*' ')
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + '  '
            for e in element:
                self.prettyXMLformater(e, level+1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + '  '
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i
        return

if __name__ == '__main__':
    print(__doc__)
