#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for uncompressed mzML files.

@author: Manuel Koesters
"""
from __future__ import print_function
import codecs
import pymzml.spec as spec
import pymzml.regex_patterns as regex_patterns
from xml.etree.ElementTree import XML, iterparse
import re
import bisect


class StandardMzml(object):
    """
    """
    def __init__(self, path, encoding):
        """
        Initalize Wrapper object for standard mzML files.

        Arguments:
            path (str)     : path to the file
            encoding (str) : encoding of the file
        """
        self.path         = path
        self.file_handler = codecs.open(
            path,
            mode     = 'r',
            encoding = encoding
        )
        self.offset_dict = dict()
        self.spec_open = regex_patterns.SPECTRUM_OPEN_PATTERN
        self.spec_close = regex_patterns.SPECTRUM_CLOSE_PATTERN

    # def __del__(self):
    #     """
    #     """
    #     pass
    #     # self.file_handler.close()

    def __getitem__(self, identifier):
        """
        Access the item with id 'identifier' in the file using
        either linear, binary or interpolated search.

        Arguments:
            identifier (str): native id of the item to access

        Returns:
            data (str): text associated with the given identifier
        """

        #############################################################################
        # DOES NOT HOLD IF NUMBERS DONT START WITH ONE AND/OR DONT INCREASE BY ONE  #
        # TODO FIXME                                                                #
        #############################################################################

        self.file_handler.seek(0)

        spectrum = None

        if str(identifier).upper() == 'TIC':
            # print(str(identifier).upper())
            found = False
            mzmliter = iter(iterparse(self.file_handler, events=['end']))
            while found is False:
                event, element = next(mzmliter, ('STOP', 'STOP'))
                if event == 'end':
                    if element.tag.endswith('}chromatogram'):
                        if element.get('id') == 'TIC':
                            found = True
                            spectrum = spec.Chromatogram(
                                element,
                                measured_precision = 5e-6
                            )
                elif event == 'STOP':
                    raise StopIteration

        elif identifier in self.offset_dict:
            start = self.offset_dict[identifier]
            with open(self.path, 'rb') as seeker:
                seeker.seek(start[0])
                start, end = self._read_to_spec_end(seeker)
            self.file_handler.seek(start, 0)
            data     = self.file_handler.read(end - start)
            spectrum = spec.Spectrum(
                XML(data),
                measured_precision = 5e-6
            )
        elif type(identifier) == str:
            return self._search_string_identifier(
                identifier
            )
        else:
            spectrum = self._interpol_search(identifier)

        return spectrum

    def _interpol_search(self, target_index, chunk_size=8, fallback_cutoff=100):
        """
        Use linear interpolation search to find spectra faster.

        Arguments:
            target_index (str or int) : native id of the item to access

        Keyword Arguments:
            chunk_size (int)        : size of the chunk to read in one go in kb

        """
        # print('target ', target_index)
        seeker          = open(self.path, 'rb')
        seeker.seek(0, 2)
        chunk_size      = chunk_size * 512
        lower_bound     = 0
        upper_bound     = seeker.tell()
        mid             = int(upper_bound / 2)
        seeker.seek(mid, 0)
        current_position = seeker.tell()
        used_indices = set()
        spectrum_found = False
        spectrum = None
        while spectrum_found is False:
            jumper_scaling = 1
            file_pointer    = seeker.tell()
            data            = seeker.read(chunk_size)
            spec_start      = self.spec_open.search(data)
            if spec_start is not None:
                spec_start_offset = file_pointer + spec_start.start()
                seeker.seek(spec_start_offset)
                current_index = int(
                    re.search(
                        b'[0-9]*$',
                        spec_start.group('id')
                    ).group()
                )

                self.offset_dict[current_index] = (spec_start_offset,)
                if current_index in used_indices:
                    # seeker.close()
                    if current_index > target_index:
                        jumper_scaling -= 0.1
                    else:
                        jumper_scaling += 0.1

                used_indices.add(current_index)

                dist = current_index - target_index
                if dist < -1 and dist > -(fallback_cutoff):
                    spectrum = self._search_linear(seeker, target_index)
                    seeker.close()
                    spectrum_found = True
                    break
                elif dist > 0 and dist < fallback_cutoff:
                    while current_index > target_index:
                        offset = int(current_position - chunk_size)
                        seeker.seek(offset if offset > 0 else 0)
                        lower_bound     = current_position
                        current_position = seeker.tell()
                        data = seeker.read(chunk_size)
                        if self.spec_open.search(data):
                            spec_start = self.spec_open.search(data)
                            current_index = int(
                                re.search(
                                    b'[0-9]*$',
                                    spec_start.group('id')
                                ).group()
                            )
                    seeker.seek(current_position)
                    spectrum = self._search_linear(seeker, target_index)
                    seeker.close()
                    spectrum_found = True
                    break

                if int(current_index) == target_index:

                    seeker.seek(spec_start_offset)
                    start, end = self._read_to_spec_end(seeker)
                    seeker.seek(start)
                    self.offset_dict[current_index] = (start, end)
                    xml_string = seeker.read(
                        end - start
                    )
                    seeker.close()
                    spectrum = spec.Spectrum(
                        XML(xml_string),
                        measured_precision=5e-6
                    )
                    spectrum_found = True
                    break

                elif int(current_index) > target_index:
                    scaling          = target_index / current_index
                    seeker.seek(int(current_position * scaling * jumper_scaling))
                    upper_bound      = current_position
                    current_position = seeker.tell()
                elif int(current_index) < target_index:
                    scaling          = target_index / current_index
                    seeker.seek(int(current_position * scaling * jumper_scaling))
                    lower_bound      = current_position
                    current_position = seeker.tell()

            elif len(data) == 0:
                sorted_keys = sorted(self.offset_dict.keys())
                pos = bisect.bisect_left(sorted_keys, target_index) - 2  # dat magic number :)
                try:
                    key = sorted_keys[pos]
                    spec_start_offset = self.offset_dict[key][0]
                except:
                    key = sorted_keys[pos]
                    spec_start_offset = self.offset_dict[key][0]
                seeker = open(self.path, 'rb')
                seeker.seek(spec_start_offset)
                spectrum = self._search_linear(seeker, target_index)
                seeker.close()
                spectrum_found = True
                break

        return spectrum

    def _read_to_spec_end(self, seeker):
        """
        Read from current seeker position to the end of the
        next spectrum tag and return start and end postition

        Args:
            seeker (_io.BufferedReader): Reader instance used in calling function

        Returns:
            positions (tuple): tuple with start and end postion of the spectrum
        """
        # start_pos = seeker.tell()
        chunk_size = 512
        end_found = False
        start_pos = seeker.tell()

        while end_found is False:
            chunk_offset = seeker.tell()
            data_chunk = seeker.read(chunk_size)
            tag_end, seeker  = self._read_until_tag_end(seeker)
            data_chunk += tag_end
            if regex_patterns.SPECTRUM_CLOSE_PATTERN.search(data_chunk):
                match = regex_patterns.SPECTRUM_CLOSE_PATTERN.search(data_chunk)
                relative_pos_in_chunk = match.end()
                end_pos = chunk_offset + relative_pos_in_chunk
                end_found = True
        return (start_pos, end_pos)

    def _search_linear(self, seeker, index, chunk_size=8):
        """
        Fallback to linear search if interpolated search fails.
        """
        data = None
        i = 0
        total_chunk_size = chunk_size * 512
        spec_start = None
        spec_end   = None
        i = 0
        # print('target', index)
        while True:
            file_pointer = seeker.tell()

            data         = seeker.read(total_chunk_size)
            string, seeker = self._read_until_tag_end(seeker)
            data += string

            spec_start    = self.spec_open.search(data)
            if spec_start:
                spec_start_offset = file_pointer + spec_start.start()
                seeker.seek(spec_start_offset)
                current_index = int(
                    re.search(
                        b'[0-9]*$',
                        spec_start.group('id')
                    ).group()
                )
                # print(current_index)
                spec_end = self.spec_close.search(data[spec_start.start():])
                if spec_end:
                    spec_end_offset = file_pointer + spec_end.end() + spec_start.start()
                    seeker.seek(spec_end_offset)
                while spec_end is None:

                    file_pointer = seeker.tell()

                    data          = seeker.read(total_chunk_size)
                    string, seeker = self._read_until_tag_end(seeker)
                    data += string

                    spec_end       = self.spec_close.search(data)
                    if spec_end:
                        spec_end_offset = file_pointer + spec_end.end()
                        self.offset_dict[current_index] = (spec_start_offset, spec_end_offset)
                        seeker.seek(spec_end_offset)
                        break

                if current_index == index:
                    seeker.seek(spec_start_offset)
                    spec_string = seeker.read(
                        spec_end_offset - spec_start_offset
                    )
                    self.offset_dict[current_index] = (
                        spec_start_offset,
                        spec_end_offset
                    )
                    xml_string = XML(spec_string)
                    seeker.close()
                    return spec.Spectrum(
                        xml_string,
                        measured_precision=5e-6
                    )

    def _search_string_identifier(self, search_string, chunk_size=8):
        with open(self.path, 'rb') as seeker:
            data = None
            total_chunk_size = chunk_size * 512
            spec_start = None

            # NOTE: This needs to go intp regex_patterns.py

            regex_string = re.compile(
                "<\s*spectrum[^>]*index=\"[0-9]+\"\sid=\"({0})\"\sdefaultArrayLength=\"[0-9]+\">".format(
                    "".join(
                        ['.*', search_string, '.*']
                    )
                ).encode()
            )

            search_string = search_string.encode()

            while True:
                file_pointer = seeker.tell()

                data         = seeker.read(total_chunk_size)
                string, seeker = self._read_until_tag_end(seeker, byte_mode=True)
                data += string
                spec_start = regex_string.search(data)
                if spec_start:
                    spec_start_offset = file_pointer + spec_start.start()
                    current_index = spec_start.group(1)
                    if search_string in current_index:
                        seeker.seek(spec_start_offset)
                        start, end = self._read_to_spec_end(seeker)
                        seeker.seek(start)
                        spec_string = seeker.read(end-start)
                        xml_string = XML(spec_string)
                        return spec.Spectrum(
                            xml_string,
                            measured_precision=5e-6
                        )
                elif len(data) == 0:
                    raise Exception('cant find specified string')

    def _read_until_tag_end(self, seeker, max_search_len=12, byte_mode=False):
        """
        Help make sure no splitted text appear in chunked data, so regex always find
        <spectrum ...>
        and
        </spectrum>
        """
        count  = 0
        string = b''
        curr_byte = ''
        while count < max_search_len and curr_byte != b'>' and curr_byte != b'<' and curr_byte != b' ':
            curr_byte = seeker.read(1)
            string += curr_byte
            count += 1
        return string, seeker

    def read(self, size=-1):
        """
        Read binary data from file handler.

        Keyword Arguments:
            size (int): Number of bytes to read from file, -1 to read to end of file

        Returns:
            data (str): byte string of len size of input data
        """
        return self.file_handler.read(size)

    def close(self):
        """
        """
        self.file_handler.close()

if __name__ == '__main__':
    print(__doc__)
