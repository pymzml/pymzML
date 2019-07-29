#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for uncompressed mzML files.

@author: Manuel Koesters
"""

import bisect
import codecs
import re
from xml.etree.ElementTree import XML, iterparse

from .. import spec
from .. import regex_patterns


class StandardMzml(object):
    """
    """

    def __init__(self, path, encoding, build_index_from_scratch=False):
        """
        Initalize Wrapper object for standard mzML files.

        Arguments:
            path (str)     : path to the file
            encoding (str) : encoding of the file
        """
        self.path = path
        self.file_handler = self.get_file_handler(encoding)
        self.offset_dict = dict()
        self.spec_open = regex_patterns.SPECTRUM_OPEN_PATTERN
        self.spec_close = regex_patterns.SPECTRUM_CLOSE_PATTERN
        if build_index_from_scratch is True:
            seeker = self.get_binary_file_handler()
            self._build_index_from_scratch(seeker)
            seeker.close()

    def get_binary_file_handler(self):
        return open(self.path, "rb")

    def get_file_handler(self, encoding):
        return codecs.open(self.path, mode="r", encoding=encoding)

    def __getitem__(self, identifier):
        """
        Access the item with id 'identifier'.

        Either use linear, binary or interpolated search.

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
        if str(identifier).upper() == "TIC":
            # print(str(identifier).upper())
            found = False
            mzmliter = iter(iterparse(self.file_handler, events=["end"]))
            while found is False:
                event, element = next(mzmliter, ("STOP", "STOP"))
                if event == "end":
                    if element.tag.endswith("}chromatogram"):
                        if element.get("id") == "TIC":
                            found = True
                            spectrum = spec.Chromatogram(
                                element, measured_precision=5e-6
                            )
                elif event == "STOP":
                    raise StopIteration

        elif identifier in self.offset_dict:

            start = self.offset_dict[identifier]
            with self.get_binary_file_handler() as seeker:
                seeker.seek(start[0])
                start, end = self._read_to_spec_end(seeker)
            self.file_handler.seek(start, 0)
            data = self.file_handler.read(end - start)
            if data.startswith("<spectrum"):
                spectrum = spec.Spectrum(XML(data), measured_precision=5e-6)
            elif data.startswith("<chromatogram"):
                spectrum = spec.Chromatogram(XML(data))
        elif type(identifier) == str:
            return self._search_string_identifier(identifier)
        else:
            spectrum = self._interpol_search(identifier)

        return spectrum

    def _build_index(self, from_scratch=False):
        """
        Build an index.

        A list of offsets to which a file pointer can seek
        directly to access a particular spectrum or chromatogram without
        parsing the entire file.

        Args:

            from_scratch(bool): Whether or not to force building the index from
                             scratch, by parsing the file, if no existing
                             index can be found.

        Returns:
            A file-like object used to access the indexed content by
            seeking to a particular offset for the file.
        """
        # Declare the pre-seeker
        seeker = self.get_binary_file_handler()
        # Reading last 1024 bytes to find chromatogram Pos and SpectrumIndex Pos
        index_list_offset_pattern = re.compile(
            b"<indexListOffset>(?P<indexListOffset>[0-9]*)</indexListOffset>"
        )
        chromatogram_offset_pattern = re.compile(
            b'(?P<WTF>[nativeID|idRef])="TIC">(?P<offset>[0-9]*)</offset'
        )
        self.offset_dict["TIC"] = None
        seeker.seek(0, 2)
        index_found = False

        spectrum_index_pattern = regex_patterns.SPECTRUM_INDEX_PATTERN
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
                match = chromatogram_offset_pattern.search(line)
                if match:
                    self.offset_dict["TIC"] = int(bytes.decode(match.group("offset")))

                match_spec = spectrum_index_pattern.search(line)
                if match_spec is not None:
                    spec_byte_offset = int(bytes.decode(match_spec.group("offset")))
                    sanity_check_set.add(spec_byte_offset)

                match = index_list_offset_pattern.search(line)
                if match:
                    index_found = True
                    # print(int(match.group('indexListOffset').decode('utf-8')))
                    # print(line)
                    # exit(1)
                    index_list_offset = int(
                        match.group("indexListOffset").decode("utf-8")
                    )
                    # break

            if index_found is True and self.offset_dict["TIC"] is not None:
                break

        if index_found is True:
            # Jumping to index list and slurpin all specOffsets
            seeker.seek(index_list_offset, 0)
            spectrum_index_pattern = regex_patterns.SPECTRUM_INDEX_PATTERN
            sim_index_pattern = regex_patterns.SIM_INDEX_PATTERN

            for line in seeker:
                match_spec = spectrum_index_pattern.search(line)
                if match_spec and match_spec.group("nativeID") == b"":
                    match_spec = None
                match_sim = sim_index_pattern.search(line)
                if match_spec:
                    offset = int(bytes.decode(match_spec.group("offset")))
                    native_id = int(bytes.decode(match_spec.group("nativeID")))
                    self.offset_dict[native_id] = offset
                elif match_sim:
                    offset = int(bytes.decode(match_sim.group("offset")))
                    native_id = bytes.decode(match_sim.group("nativeID"))
                    # if native_id == 'DECOY_126104_C[160]NVVISGGTGSGK/2_y10':
                    try:
                        native_id = int(
                            regex_patterns.SPECTRUM_ID_PATTERN.search(native_id).group(
                                1
                            )
                        )
                        # exit(1)
                    except AttributeError:
                        # match is None and has no attribute group,
                        # so use the whole string as ID
                        pass
                    self.offset_dict[native_id] = (offset,)
        seeker.close()

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
            chromexp = re.compile(b'<\s*chromatogram[^>]*id="([^"]*)"')
            chromcntexp = re.compile(b'<\s*chromatogramList\s*count="([^"]*)"')
            specexp = re.compile(b'<\s*spectrum[^>]*id="([^"]*)"')
            speccntexp = re.compile(b'<\s*spectrumList\s*count="([^"]*)"')
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
                    chrom_positions[m.group(1).decode("utf-8")] = offset + m.start()
                for m in specexp.finditer(chunk):
                    spec_positions[m.group(1).decode("utf-8")] = offset + m.start()

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
            if chromcnt == len(chrom_positions) and speccnt == len(spec_positions):
                positions = {}
                positions.update(chrom_positions)
                positions.update(spec_positions)
            else:
                print(
                    "[ Warning ] Found {spec_count} spectra "
                    "and {chrom_count} chromatograms\n"
                    "[ Warning ] However Spectrum index list shows {speccnt} and "
                    "Chromatogram index list shows {chromcnt} entries".format(
                        spec_count=len(spec_positions),
                        chrom_count=len(chrom_positions),
                        speccnt=speccnt,
                        chromcnt=chromcnt,
                    )
                )
                print(
                    "[ Warning ] Updating offset dict with found offsets "
                    "but some might be still missing\n"
                    "[ Warning ] This may happen because your is file truncated"
                )
                positions = {}
                positions.update(chrom_positions)
                positions.update(spec_positions)
            return positions

        indices = get_data_indices(seeker)
        if indices is not None:
            tmp_dict = {}

            item_list = sorted(list(indices.items()), key=lambda x: x[1])
            for i in range(len(item_list)):
                key = item_list[i][0]
                tmp_dict[key] = (item_list[i][1],)

            self.offset_dict.update(tmp_dict)

            # make sure the list is sorted (for bisect)
            # self.info['offsetList'] = sorted(self.info['offsetList'])
            # self.info['seekable'] = True

        return

    def _interpol_search(self, target_index, chunk_size=8, fallback_cutoff=100):
        """
        Use linear interpolation search to find spectra faster.

        Arguments:
            target_index (str or int) : native id of the item to access

        Keyword Arguments:
            chunk_size (int)        : size of the chunk to read in one go in kb

        """
        # print('target ', target_index)
        seeker = self.get_binary_file_handler()
        seeker.seek(0, 2)
        chunk_size = chunk_size * 512
        lower_bound = 0
        upper_bound = seeker.tell()
        mid = int(upper_bound / 2)
        seeker.seek(mid, 0)
        current_position = seeker.tell()
        used_indices = set()
        spectrum_found = False
        spectrum = None
        while spectrum_found is False:
            jumper_scaling = 1
            file_pointer = seeker.tell()
            data = seeker.read(chunk_size)
            spec_start = self.spec_open.search(data)
            if spec_start is not None:
                spec_start_offset = file_pointer + spec_start.start()
                seeker.seek(spec_start_offset)
                current_index = int(
                    re.search(b"[0-9]*$", spec_start.group("id")).group()
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
                        lower_bound = current_position
                        current_position = seeker.tell()
                        data = seeker.read(chunk_size)
                        if self.spec_open.search(data):
                            spec_start = self.spec_open.search(data)
                            current_index = int(
                                re.search(b"[0-9]*$", spec_start.group("id")).group()
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
                    xml_string = seeker.read(end - start)
                    seeker.close()
                    spectrum = spec.Spectrum(XML(xml_string), measured_precision=5e-6)
                    spectrum_found = True
                    break

                elif int(current_index) > target_index:
                    scaling = target_index / current_index
                    seeker.seek(int(current_position * scaling * jumper_scaling))
                    upper_bound = current_position
                    current_position = seeker.tell()
                elif int(current_index) < target_index:
                    scaling = target_index / current_index
                    seeker.seek(int(current_position * scaling * jumper_scaling))
                    lower_bound = current_position
                    current_position = seeker.tell()

            elif len(data) == 0:
                sorted_keys = sorted(self.offset_dict.keys())
                pos = (
                    bisect.bisect_left(sorted_keys, target_index) - 2
                )  # dat magic number :)
                try:
                    key = sorted_keys[pos]
                    spec_start_offset = self.offset_dict[key][0]
                except:
                    key = sorted_keys[pos]
                    spec_start_offset = self.offset_dict[key][0]
                seeker = self.get_binary_file_handler()
                seeker.seek(spec_start_offset)
                spectrum = self._search_linear(seeker, target_index)
                seeker.close()
                spectrum_found = True
                break

        return spectrum

    def _read_to_spec_end(self, seeker, chunks_to_read=8):
        """
        Read from current seeker position to the end of the
        next spectrum tag and return start and end postition

        Args:
            seeker (_io.BufferedReader): Reader instance used in calling function

        Returns:
            positions (tuple): tuple with start and end postion of the spectrum
        """
        # start_pos = seeker.tell()
        chunk_size = 512 * chunks_to_read
        end_found = False
        start_pos = seeker.tell()
        data_chunk = seeker.read(chunk_size)
        while end_found is False:
            chunk_offset = seeker.tell()
            data_chunk = seeker.read(chunk_size)
            tag_end, seeker = self._read_until_tag_end(seeker)
            data_chunk += tag_end
            if regex_patterns.SPECTRUM_CLOSE_PATTERN.search(data_chunk):
                match = regex_patterns.SPECTRUM_CLOSE_PATTERN.search(data_chunk)
                relative_pos_in_chunk = match.end()
                end_pos = chunk_offset + relative_pos_in_chunk
                end_found = True
            elif regex_patterns.CHROMATOGRAM_CLOSE_PATTERN.search(data_chunk):
                match = regex_patterns.CHROMATOGRAM_CLOSE_PATTERN.search(data_chunk)
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
        spec_end = None
        i = 0
        # print('target', index)
        while True:
            file_pointer = seeker.tell()

            data = seeker.read(total_chunk_size)
            string, seeker = self._read_until_tag_end(seeker)
            data += string

            spec_start = self.spec_open.search(data)
            if spec_start:
                spec_start_offset = file_pointer + spec_start.start()
                seeker.seek(spec_start_offset)
                current_index = int(
                    re.search(b"[0-9]*$", spec_start.group("id")).group()
                )
                # print(current_index)
                spec_end = self.spec_close.search(data[spec_start.start() :])
                if spec_end:
                    spec_end_offset = file_pointer + spec_end.end() + spec_start.start()
                    seeker.seek(spec_end_offset)
                while spec_end is None:

                    file_pointer = seeker.tell()

                    data = seeker.read(total_chunk_size)
                    string, seeker = self._read_until_tag_end(seeker)
                    data += string

                    spec_end = self.spec_close.search(data)
                    if spec_end:
                        spec_end_offset = file_pointer + spec_end.end()
                        self.offset_dict[current_index] = (
                            spec_start_offset,
                            spec_end_offset,
                        )
                        seeker.seek(spec_end_offset)
                        break

                if current_index == index:
                    seeker.seek(spec_start_offset)
                    spec_string = seeker.read(spec_end_offset - spec_start_offset)
                    self.offset_dict[current_index] = (
                        spec_start_offset,
                        spec_end_offset,
                    )
                    xml_string = XML(spec_string)
                    seeker.close()
                    return spec.Spectrum(xml_string, measured_precision=5e-6)

    def _search_string_identifier(self, search_string, chunk_size=8):
        with self.get_binary_file_handler() as seeker:
            data = None
            total_chunk_size = chunk_size * 512
            spec_start = None

            # NOTE: This needs to go intp regex_patterns.py

            regex_string = re.compile(
                '<\s*spectrum[^>]*index="[0-9]+"\sid="({0})"\sdefaultArrayLength="[0-9]+">'.format(
                    "".join([".*", search_string, ".*"])
                ).encode()
            )

            search_string = search_string.encode()

            while True:
                file_pointer = seeker.tell()

                data = seeker.read(total_chunk_size)
                string, seeker = self._read_until_tag_end(seeker, byte_mode=True)
                data += string
                spec_start = regex_string.search(data)
                chrom_start = regex_patterns.CHROMO_OPEN_PATTERN.search(data)
                if spec_start:
                    spec_start_offset = file_pointer + spec_start.start()
                    current_index = spec_start.group(1)
                    if search_string in current_index:
                        seeker.seek(spec_start_offset)
                        start, end = self._read_to_spec_end(seeker)
                        seeker.seek(start)
                        spec_string = seeker.read(end - start)
                        xml_string = XML(spec_string)
                        return spec.Spectrum(xml_string, measured_precision=5e-6)
                elif chrom_start:
                    chrom_start_offset = file_pointer + chrom_start.start()
                    if search_string == chrom_start.group(1):
                        seeker.seek(chrom_start_offset)
                        start, end = self._read_to_spec_end(seeker)
                        seeker.seek(start)
                        chrom_string = seeker.read(end - start)
                        xml_string = XML(chrom_string)
                        return spec.Chromatogram(xml_string)
                elif len(data) == 0:
                    raise Exception("cant find specified string")

    def _read_until_tag_end(self, seeker, max_search_len=12, byte_mode=False):
        """
        Help make sure no splitted text appear in chunked data, so regex always find
        <spectrum ...>
        and
        </spectrum>
        """
        count = 0
        string = b""
        curr_byte = ""
        while (
            count < max_search_len
            and curr_byte != b">"
            and curr_byte != b"<"
            and curr_byte != b" "
        ):
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


if __name__ == "__main__":
    print(__doc__)
