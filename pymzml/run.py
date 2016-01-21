# -*- coding: utf-8 -*-
# encoding: utf-8
"""
The class :py:class:`Reader` has been designed to selectively extract data
from a mzML file and to expose the data as a python object.
Necessary information are read in and stored in a fast
accessible format.
The reader itself is an iterator, thus looping over all spectra
follows the classical pythonian syntax.
Additionally one can random access spectra by their nativeID
if the file if not compressed or truncated by a conversion Program.

The class :py:class:`Writer` is still in development.

"""

# pymzml
#
# Copyright (C) 2010-2014 T. Bald, J. Barth, A. Niehues, M. Specht, H. Roest, C. Fufezan
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

import re
import os
import bisect
import codecs

from xml.etree import cElementTree

from collections import defaultdict as ddict

import pymzml.spec

import pymzml.obo
import pymzml.minimum


class RegexPatterns(object):
    spectrumIndexPattern = re.compile(
        b'(?P<type>(scan=|nativeID="))(?P<nativeID>[0-9]*)">(?P<offset>[0-9]*)</offset>'
    )
    simIndexPattern = re.compile(b'(?P<type>idRef=")(?P<nativeID>.*)">(?P<offset>[0-9]*)</offset>')


class Reader(object):
    """
    .. function:: __init__(
        path*
        [,noiseThreshold=0.0, extraAccessions=None, MS1_Precision=5e-6, MSn_Precision=20e-6]
    )

    Initializes an mzML run and returns an iterator.

    :param path: path to mzML file. File can be gzipped.
    :type path: string

    :param extraAccessions: list of additional (accession,fieldName) tuples.


        For example, ('MS:1000285',['value']) will extract the "total ion
        current" and store it under two keys in the spectrum, i.e.
        spectrum["total ion current"] or spectrum['MS:1000285'].

        The translated name is extracted from the current OBO file,
        hence the name that is defined by the HUPO-PSI consortium is used.
        (http://www.psidev.info/).

        pymzML comes with an example script queryOBO.py which can be used to
        lookup the names or MS tags (see: :py:obj:`queryOBO`).

        The value, i.e. which xml property has to be extraced has to be provided
        by the user. Multiple values can be used as input, i.e. ( 'MS:1000016' ,
        ['value','unitName'] ) will extract scan time and its unit.

    :type extraAccessions: list of tuples
    :param MS1_Precision: measured precision of MS1 spectra
    :type MS1_Precision: float
    :param MSn_Precision: measured precision of MSn spectra
    :type MSn_Precision: float
    :param build_index_from_scratch: build index from scratch
    :type build_index_from_scratch: boolean
    :param file_object: file object or any other iterable stream, this will make
                        path obsolete, seeking is disabled
    :type file_object: File_object like

    Example:

    >>> run = pymzml.run.Reader("../mzML_example_files/100729_t300_100729172744.mzML.gz",
                                MS1_Precision = 20e-6)
    """

    def __init__(
        self,
        path=None,
        noiseThreshold=0.0,
        extraAccessions=None,
        MS1_Precision=5e-6,
        MSn_Precision=20e-6,
        build_index_from_scratch=False,
        file_object=None,
        obo_version=None,
        use_spectra_sanity_check=True,
    ):
        # self.param contains user-specified parsing parameters
        self.param = dict()

        self.param['noiseThreshold'] = noiseThreshold
        self.param['MS1_Precision'] = MS1_Precision
        self.param['MSn_Precision'] = MSn_Precision
        self.param['accessions'] = {}

        # self.info contains information extracted from the mzML file
        self.info = dict()

        self.info['offsets'] = ddict()
        self.info['offsetList'] = []
        self.info['referenceableParamGroupList'] = False

        self.info['spectrum_count'] = 0
        self.info['chromatogram_count'] = 0

        self.info['obo_version'] = obo_version

        self.info['encoding'] = None

        self.MS1_Precision = MS1_Precision

        self.elementList = []

        # Default stuff

        # Can actually be either a spectrum _or_ a chromatogram; the Spectrum
        # class supports both
        self.spectrum = pymzml.spec.Spectrum(
            measuredPrecision=MS1_Precision,
            param=self.param,
        )
        self.spectrum.clear()

        assert path is not None or file_object is not None, \
            'Must provide either a path or a file object to parse'

        self.info['fileObject'], self.info['seekable'] = self.__open_file(
            path,
            file_object
        )
        self.info['filename'] = path

        if self.info['seekable']:
            # Seekable files can use the index for random access
            self.seeker = self._build_index(build_index_from_scratch, use_spectra_sanity_check)

        self.iter = self.__init_iter()
        self.OT = self.__init_obo_translator(extraAccessions)
        return

    def __determine_file_encoding(self, path):
        '''
        Determines mzML XML encoding using the information in the
        first line of the mzML. Otherwise falls back to utf-8.

        '''
        mzML_encoding = 'utf-8'
        if os.path.exists( path ):
            # we might have been initialized with a file-object
            # then no questions about the encoding have to be addressed
            # is not seekable neither ..
            sniffer = open(path, 'rb')
            header = sniffer.readline()
            encodingPattern = re.compile(
                b'encoding="(?P<encoding>[A-Za-z0-9-]*)"'
            )
            match = encodingPattern.search(header)
            if match:
                mzML_encoding = bytes.decode(
                    match.group('encoding')
                )
            sniffer.close()
        return mzML_encoding

    def _open_file(self, path, given_file_object=None):
        return self.__open_file( path, given_file_object=given_file_object)

    def __open_file(self, path, given_file_object=None):
        # Arbitrary supplied file objects are not seekable
        file_object = given_file_object
        seekable = False
        self.info['encoding'] = self.__determine_file_encoding( path )
        if file_object is None:
            import codecs
            if path.endswith('.gz'):
                # Gzipped files are not seekable
                import gzip
                file_object = codecs.getreader("utf-8")(
                    gzip.open(path)
                )
            else:
                file_object = codecs.open(
                    path,
                    mode     = 'r',
                    encoding = self.info['encoding']
                )
                seekable = True

        return file_object, seekable

    def _build_index(self, from_scratch, use_spectra_sanity_check):
        """
        .. method:: _build_index(from_scratch)

        Builds an index: a list of offsets to which a file pointer can seek
        directly to access a particular spectrum or chromatogram without
        parsing the entire file.

        :param from_scratch: Whether or not to force building the index from
                             scratch, by parsing the file, if no existing
                             index can be found.
        :type from_scratch: A boolean

        :param use_spectra_sanity_check: Whether or not to assume all data are
                                         spectra and follow the (scan=|nativeID=") 
                                         pattern. Disable this if you have
                                         chromatograms or spectra with
                                         different ids.
        :type from_scratch: A boolean

        :returns: A file-like object used to access the indexed content by
                  seeking to a particular offset for the file.
        """

        # Declare the pre-seeker
        seeker = open(self.info['filename'], 'rb')
        # Reading last 1024 bytes to find chromatogram Pos and SpectrumIndex Pos
        indexListOffsetPattern = re.compile(
            b'<indexListOffset>(?P<indexListOffset>[0-9]*)</indexListOffset>'
        )
        chromatogramOffsetPattern = re.compile(
            b'(?P<WTF>[nativeID|idRef])="TIC">(?P<offset>[0-9]*)</offset'
        )
        self.info['offsets']['indexList'] = None
        self.info['offsets']['TIC'] = None
        seeker.seek(0, 2)
        spectrumIndexPattern = RegexPatterns.spectrumIndexPattern
        for _ in range(1, 10):  # max 10kbyte
            # some converters fail in writing a correct index
            # we found
            # a) the offset is always the same (silent fail hurray!)
            sanity_check_set = set()
            try:
                seeker.seek(-1024 * _, 1)
            except:
                break
                # File is smaller than 10kbytes ...
            for line in seeker:
                match = chromatogramOffsetPattern.search(line)
                if match:
                    self.info['offsets']['TIC'] = int(
                        bytes.decode(match.group('offset'))
                    )

                match_spec = spectrumIndexPattern.search(line)
                if match_spec is not None:
                    spec_byte_offset = int(
                        bytes.decode(match_spec.group('offset'))
                    )
                    sanity_check_set.add(spec_byte_offset)

                match = indexListOffsetPattern.search(line)
                if match:
                    self.info['offsets']['indexList'] = int(
                        bytes.decode(match.group('indexListOffset'))
                    )
                    # break

            if self.info['offsets']['indexList'] is not None and \
                    self.info['offsets']['TIC'] is not None:
                break

        if use_spectra_sanity_check and len(sanity_check_set) <= 2:
            # print( 'Convert error obvious ... ')
            self.info['offsets']['indexList'] = None

        if self.info['offsets']['indexList'] is None:
            # fall back to non-seekable
            self.info['seekable'] = False
            if from_scratch:
                self._build_index_from_scratch(seeker)
        elif self.info['offsets']['TIC'] is not None and \
                self.info['offsets']['TIC'] > os.path.getsize(self.info['filename']):
            self.info['seekable'] = False
        else:
            # Jumping to index list and slurpin all specOffsets
            seeker.seek(self.info['offsets']['indexList'], 0)
            spectrumIndexPattern = RegexPatterns.spectrumIndexPattern
            simIndexPattern = RegexPatterns.simIndexPattern

            # NOTE: this might be again different in another mzML versions!!
            # 1.1 >> small_zlib.pwiz.1.1.mzML:
            #   <offset idRef="controllerType=0 controllerNumber=1 scan=1">4363</offset>
            # 1.0 >>
            #   <offset idRef="S16004" nativeID="16004">236442042</offset>
            #   <offset idRef="SIM SIC 651.5">330223452</offset>\n'
            for line in seeker:
                match_spec = spectrumIndexPattern.search(line)
                if match_spec and match_spec.group('nativeID') == b'':
                    match_spec = None
                match_sim = simIndexPattern.search(line)
                if match_spec:
                    offset = int(bytes.decode(match_spec.group('offset')))
                    nativeID = int(bytes.decode(match_spec.group('nativeID')))
                    self.info['offsets'][nativeID] = offset
                    self.info['offsetList'].append(offset)
                elif match_sim:
                    offset = int(bytes.decode(match_sim.group('offset')))
                    nativeID = bytes.decode(match_sim.group('nativeID'))
                    try:
                        nativeID = int(nativeID)
                    except:
                        pass
                    self.info['offsets'][nativeID] = offset
                    self.info['offsetList'].append(offset)
            # opening seeker in normal mode again
        seeker.close()
        seeker = codecs.open(
            self.info['filename'],
            mode     = 'r',
            encoding = self.info['encoding']
        )
        # seeker = open(self.info['filename'], 'r')

        return seeker

    def _build_index_from_scratch(self, seeker):
        """Build an index of spectra/chromatogram data with offsets by parsing the file."""

        def get_data_indices(fh, chunksize=8192, lookback_size=100):
            """Get a dictionary with binary file indices of spectra and
            chromatograms in an mzML file.

            Will parse quickly through the file and find all occurences of
            <chromatogram ... id="..." and <spectrum ... id="..." using a
            regex.
            We dont use an XML parser here because we need to know the
            exact location of the filepointer which is usually not possible
            with common xml parsers.
            """
            chrom_positions = {}
            spec_positions = {}
            chromcnt = 0
            speccnt = 0
            # regexes to be used
            chromexp = re.compile(b"<\s*chromatogram[^>]*id=\"([^\"]*)\"")
            chromcntexp = re.compile(b"<\s*chromatogramList\s*count=\"([^\"]*)\"")
            specexp = re.compile(b"<\s*spectrum[^>]*id=\"([^\"]*)\"")
            speccntexp = re.compile(b"<\s*spectrumList\s*count=\"([^\"]*)\"")
            # go to start of file
            fh.seek(0)
            prev_chunk = ""
            while True:
                 # read a chunk of data
                offset = fh.tell()
                chunk = fh.read(chunksize)
                if not chunk:
                    break

                 # append a part of the previous chunk since we have cut in the middle
                 # of the text (to make sure we dont miss anything, prev_chunk
                 # is analyzed twice).
                if len(prev_chunk) > 0:
                    chunk = prev_chunk[-lookback_size:] + chunk
                    offset -= lookback_size
                prev_chunk = chunk

                # find all occurences of the expressions and add to the dictionary
                for m in chromexp.finditer(chunk):
                    chrom_positions[m.group(1).decode('utf-8')] = offset + m.start()
                for m in specexp.finditer(chunk):
                    spec_positions[m.group(1).decode('utf-8')] = offset + m.start()

                # also look for the total count of chromatograms and spectra
                # -> must be the same as the content of our dict!
                m = chromcntexp.search(chunk)
                if m is not None:
                    chromcnt = int(m.group(1))
                m = speccntexp.search(chunk)
                if m is not None:
                    speccnt = int(m.group(1))

            # Check if everything is ok (e.g. we found the right number of
            # chromatograms and spectra) and then return the dictionary.
            if (chromcnt == len(chrom_positions) and speccnt == len(spec_positions)):
                positions = {}
                positions.update(chrom_positions)
                positions.update(spec_positions)
                # return positions # return only once in function leaves my brain sane :)
                self.info['spectrum_count'] = speccnt
                self.info['chromatogram_count'] = chromcnt

            else:
                positions = None
            return positions

        indices = get_data_indices(seeker)
        if indices is not None:
            self.info['offsets'].update(indices)
            self.info['offsetList'].extend(indices.values())

            # make sure the list is sorted (for bisect)
            self.info['offsetList'] = sorted(self.info['offsetList'])
            self.info['seekable'] = True

        return

    def __init_iter(self):
        """
        .. method:: __init_iter()

        initializes the iterator for the mzml xml parsing and moves it to the
        first relevant item.

        :returns: an iterator.
        """

        # declare the iter
        mzml_iter = iter(cElementTree.iterparse(
            self.info['fileObject'],
            events=(b'start', b'end')
        ))  # NOTE: end might be sufficient

        # Move iter to spectrumList / chromatogramList, setting the version
        # along the way
        while True:
            event, element = next(mzml_iter)
            if element.tag.endswith('}mzML'):
                if 'version' in element.attrib and len(element.attrib['version']) > 0:
                    self.info['mzmlVersion'] = element.attrib['version']
                else:
                    s = element.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation']
                    self.info['mzmlVersion'] = re.search(r'[0-9]*\.[0-9]*\.[0-9]*', s).group()
            elif element.tag.endswith('}cv'):
                if not self.info['obo_version'] and element.attrib['id'] == 'MS':
                    self.info['obo_version'] = element.attrib.get('version', '1.1.0')
            elif element.tag.endswith('}referenceableParamGroupList'):
                self.info['referenceableParamGroupList'] = True
                self.info['referenceableParamGroupListElement'] = element
            elif element.tag.endswith('}spectrumList'):
                speccnt = element.attrib.get('count')
                self.info['spectrum_count'] = int(speccnt) if speccnt else None
                break
            elif element.tag.endswith('}chromatogramList'):
                chromcnt = element.attrib.get('count')
                self.info['chromatogram_count'] = int(chromcnt) if chromcnt else None
                break
            else:
                pass

        return mzml_iter

    def __init_obo_translator(self, extraAccessions):
        """
        .. method:: __init_obo_translator(extraAccessions)

        Initializes the OBO translator of this parser

        :param extraAccessions: list of additional (accession,fieldName) tuples,
        from the constructor
        :type extraAccessions: list of tuples

        :returns: A pymzml.obo.oboTranslator object
        """

        # parse obo, check MS tags and if they are ok in minimum.py (minimum required) ...
        obo_translator = pymzml.obo.oboTranslator(version=self.info['obo_version'])

        for minimumMS, ListOfvaluesToExtract in pymzml.minimum.MIN_REQ:
            self.param['accessions'][minimumMS] = {
                'valuesToExtract': ListOfvaluesToExtract,
                'name': obo_translator[minimumMS],
                'values': []
            }

        # parse extra accessions ...
        if extraAccessions is not None:
            for accession, fieldIdentifiers in extraAccessions:
                if accession not in self.param['accessions'].keys():
                    self.param['accessions'][accession] = {
                        'valuesToExtract': [],
                        'name': obo_translator[accession],
                        'values': []
                    }
                for valueToExtract in fieldIdentifiers:
                    if valueToExtract not in self.param['accessions'][accession]['valuesToExtract']:
                        self.param['accessions'][accession]['valuesToExtract'].append(
                            valueToExtract
                        )

        return obo_translator

    def __iter__(self):
        return self

    def __next__(self):
        """ The python 2.6+ iterator """
        return self.next()

    def next(self):
        """
        Iterator for the class :py:class:`Run`:. Iterates over all of the spectra
        or chromatograms in the file.

        :return: a spectrum, stored in run.spectrum.
        :rtype: :py:class:`spec.Spectrum`:

        Example:

        >>> for spectrum in run:
        ...     print(spectrum['id'], end='\\r')

        """
        while True:
            event, element = next(self.iter, ('END', 'END'))
            # Error? check cElementTree; conversion of data to 32bit-float mzml
            # files might help

            # Stop iteration when parsing is done
            if event == 'END':
                raise StopIteration

            if (
                (element.tag.endswith('}spectrum') or element.tag.endswith('}chromatogram'))
                and event == b'end'
            ):
                if self.info['referenceableParamGroupList']:
                    self.spectrum.initFromTreeObjectWithRef(
                        element,
                        self.info['referenceableParamGroupListElement']
                    )
                else:
                    self.spectrum.initFromTreeObject(element)

                try:
                    self.elementList[-1].clear()
                except:
                    pass

                self.elementList.append(element)

                return self.spectrum

    def __getitem__(self, value):
        '''
        Random access to spectra if mzML fill is indexed,
        not compressed and not truncted.

        Example:

        >>> spectrum_with_nativeID_100 = msrun[100]

        '''
        answer = None
        if self.info['seekable'] is True:
            if len(self.info['offsets']) == 0:
                raise IOError("File does support random access: index list missing...")

            if value in self.info['offsets']:
                startPos = self.info['offsets'][value]
                endPos_index = bisect.bisect_right(
                    self.info['offsetList'],
                    self.info['offsets'][value]
                )
                if endPos_index == len(self.info['offsetList']):
                    endPos = os.path.getsize(self.info['filename'])
                else:
                    endPos = self.info['offsetList'][endPos_index]

                self.seeker.seek(startPos, 0)
                data = self.seeker.read(endPos - self.info['offsets'][value])
                try:
                    self.spectrum.initFromTreeObject(cElementTree.fromstring(data))
                except:
                    # have closing </mzml> & </run> &or </spectrumList>
                    startingTag = data.split()[0]
                    stopIndex = data.index('</' + startingTag[1:] + '>')
                    self.spectrum.initFromTreeObject(
                        cElementTree.fromstring(data[:stopIndex + len(startingTag) + 2])
                    )
                answer = self.spectrum
        else:
            # Reopen the file from the beginning if possible
            force_seeking = self.info.get('force_seeking', False)
            if force_seeking is False:
                self.info['fileObject'].close()

                assert self.info['filename'], \
                    'Must specify either filename or index for random spectrum access'
                self.info['fileObject'], _ = self.__open_file(self.info['filename'])
                self.iter = self.__init_iter()

                for spec in self:
                    if spec['id'] == value:
                        answer = spec
                        break

        if answer is None:
            raise KeyError("Run does not contain spec with native ID {0}".format(value))
        else:
            return answer

    def getSpectrumCount(self):
        return self.info['spectrum_count']

    def getChromatogramCount(self):
        return self.info['chromatogram_count']


class Writer(object):
    """
    .. function:: __init__(filename* ,run* [, overwrite = boolean])

    Initializes an mzML writer (beta stage).

    :param path: filename for the new mzML file.
    :type path: string
    :param run: Currently a pymzml.run.Reader object is required since we do
                not write the header by ourselves yet.
    :type run: pymzml.run.Reader
    :param overwrite: force the re-initialization of mzML file, even if file exists.
    :type overwrite: boolean

    At the moment no index is written.

    Example:

    >>> run = pymzml.run.Reader(
    ...     '../mzML_example_files/100729_t300_100729172744.mzML',
    ...     MS1_Precision=5e-6,
    ... )
    >>> run2 = pymzml.run.Writer(filename='write_test.mzML', run=run , overwrite=True)
    >>> spec = run[1000]
    >>> run2.addSpec(spec)
    >>> run2.save()

    """
    def __init__(self, filename=None, run=None, overwrite=False):

        cElementTree.register_namespace("", "http://psi.hupo.org/ms/mzml")
        self.filename = filename
        self.lookup = {}

        self.newTree = None
        self.TreeBuilder = cElementTree.TreeBuilder()
        self.run = run
        self.info = {'counters': ddict(int)}

        if self.run.info['filename'].endswith('.gz'):
            import gzip
            import codecs
            io = codecs.getreader("utf-8")(gzip.open(self.run.info['filename']))
        else:
            io = open(self.run.info['filename'], 'r')

        #read the rest as original file
        input_xml_string = ''
        pymzml_tag_written = False
        #open again to read as text!
        for line in open(self.run.info['filename'], 'r').readlines():
            if 'indexedmzML' in line:
                # writing of indexed mzML is not possible at the moment
                continue
            if 'run' in line:
                # the run is appended from the original parser to avoid messing
                # with the new xml tree, we break before the run data starts
                break

            input_xml_string += line
            if 'softwareList' in line and pymzml_tag_written is False:
                addon =  cElementTree.Element(
                    'software',
                    {
                        'id'      : 'pymzML',
                        'version' : "0.7.6"
                    }
                )
                cElementTree.SubElement(
                    addon,
                    'cvParam',
                    {
                        'accession' : 'MS:1000531',
                        'cvRef'     : 'MS',
                        'name'      : 'pymzML Writer',
                        'version'   : '0.7.6',
                    }
                )
                new_line = cElementTree.tostring(addon, encoding='utf-8')
                input_xml_string += new_line
                pymzml_tag_written = True
        input_xml_string += '</mzML>\n'

        self.newTree = cElementTree.fromstring(input_xml_string)

        for event, element in cElementTree.iterparse(io, events=(b'start', b'end')):
            if event ==b'start':
                if element.tag.endswith('}run'):
                    self.lookup['run'] = cElementTree.Element(element.tag, element.attrib)
                if element.tag.endswith('}spectrumList'):
                    self.lookup['spectrumList'] = \
                        cElementTree.Element(element.tag, element.attrib)
                    self.lookup['spectrumIndeces'] = \
                        cElementTree.Element('index', {'name': 'spectrum'})
                    break
        return

    def addSpec(self, spec):
        self._addTree(spec.deRef(), typeOfSpec='spectrum')
        return

    def addChromatogram(self, spec):
        self._addTree(spec.deRef(), typeOfSpec='chromatogram')
        return

    def _addTree(self, spec, typeOfSpec=None):
        if not self.lookup.has_key('{0}List'.format(typeOfSpec)):
            self.lookup['{0}List'.format(typeOfSpec)] = \
                cElementTree.Element('{0}List'.format(typeOfSpec), {'count': 0})
            self.lookup['{0}Indeces'.format(typeOfSpec)] = \
                cElementTree.Element('index', {'name': typeOfSpec})

        self.lookup[typeOfSpec + 'List'].append(spec._xmlTree)
        offset = cElementTree.Element('offset')
        offset.text = '0'
        offset.attrib = {'idRef': 'NaN', 'nativeID': str(spec['id'])}
        self.lookup[typeOfSpec + 'Indeces'].append(offset)

        self.info['counters'][typeOfSpec] += 1

        return

    def save(self):
        for typeOfSpec in ['spectrum', 'chromatogram']:
            if typeOfSpec + 'List' in self.lookup.keys():
                self.lookup['{0}List'.format(typeOfSpec)].set(
                    'count', str(self.info['counters'][typeOfSpec]),
                )
                if typeOfSpec == 'spectrum':
                    self.lookup['{0}List'.format(typeOfSpec)].set(
                        'defaultDataProcessingRef',
                        "pwiz_Reader_Thermo_conversion",
                    )
                self.lookup['run'].append(self.lookup[typeOfSpec + 'List'])
                
        self.newTree.append(
            self.lookup['run']
        )

        # IndexList = cElementTree.Element('IndexList', {
        #     'count': str(len(self.info['counters'].keys()))
        # })

        # for typeOfSpec in ['spectrum', 'chromatogram']:
        #     if typeOfSpec + 'Indeces' in self.lookup.keys():
        #         IndexList.append(self.lookup['{0}Indeces'.format(typeOfSpec)])
        # self.newTree.append(IndexList)

        self.prettyXMLformater(
            self.newTree
        )
        self.xmlTree = cElementTree.ElementTree(
            self.newTree
        )
        self.xmlTree.write(
            self.filename,
            encoding        = "utf-8",
            xml_declaration = True
        )

        return

    def prettyXMLformater(self, element, level=0):
        # Modified version from
        # http://infix.se/2007/02/06/gentlemen-indent-your-xml
        # which is a modified version of
        # http://effbot.org/zone/element-lib.htm#prettyprint

        i = '\n{0}'.format(level * ' ')
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + '  '
            for e in element:
                self.prettyXMLformater(e, level + 1)
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
