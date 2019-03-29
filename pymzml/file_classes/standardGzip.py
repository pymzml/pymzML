#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for gzipped mzML files.
"""
import codecs
import gzip
from xml.etree.ElementTree import iterparse

from .. import regex_patterns
from .. import spec


class StandardGzip(object):
    def __init__(self, path, encoding):
        """
        Initalize Wrapper object for gzipped mzML files.

        Arguments:
            path (str)     : path to the file
            encoding (str) : encoding of the file
        """
        self.path = path
        self.file_handler = codecs.getreader(encoding)(gzip.open(path))
        self.offset_dict = self._build_index()
        return

    def close(self):
        self.file_handler.close()

    def _build_index(self):
        """
        Cant build index for standard gzip files
        """
        # raise Exception('Cant build index for gzip files')
        pass

    def read(self, size=-1):
        """
        Read binary data from file handler.

        Keyword Arguments:
            size (int): Number of bytes to read from file, -1 to read to end of file

        Returns:
            data (str): byte string of len size of input data
        """
        return self.file_handler.read(size)

    def __getitem__(self, identifier):
        """
        Access the item with id 'identifier' in the file by iterating the xml-tree.

        Arguments:
            identifier (str): native id of the item to access

        Returns:
            data (str): text associated with the given identifier
        """
        old_pos = self.file_handler.tell()
        self.file_handler.seek(0, 0)
        mzml_iter = iter(iterparse(self.file_handler, events=["end"]))
        while True:
            event, element = next(mzml_iter)
            if event == "end":
                if element.tag.endswith("}spectrum"):
                    if (
                        int(
                            regex_patterns.SPECTRUM_ID_PATTERN.search(
                                element.get("id")
                            ).group(1)
                        )
                        == identifier
                    ):
                        self.file_handler.seek(old_pos, 0)
                        return spec.Spectrum(element, measured_precision=5e-6)
                elif element.tag.endswith("}chromatogram"):
                    if element.get("id") == identifier:
                        self.file_handler.seek(old_pos, 0)
                        return spec.Chromatogram(element, measured_precision=5e-6)


if __name__ == "__main__":
    print(__doc__)
