#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for binary streams of uncompressed mzML.

@author: Sylvain Le Bon
"""
from io import TextIOWrapper

from .. import regex_patterns
from .standardMzml import StandardMzml


class BytesMzml(StandardMzml):
    def __init__(self, binary, encoding, build_index_from_scratch=False):
        """
        Initalize Wrapper object for standard mzML files.

        Arguments:
            path (str)     : path to the file
            encoding (str) : encoding of the file
        """
        self.binary = binary
        self.file_handler = self.get_file_handler(encoding)
        self.offset_dict = dict()
        self.spec_open = regex_patterns.SPECTRUM_OPEN_PATTERN
        self.spec_close = regex_patterns.SPECTRUM_CLOSE_PATTERN
        if build_index_from_scratch is True:
            seeker = self.get_binary_file_handler()
            self._build_index_from_scratch(seeker)
            seeker.close()

    def get_binary_file_handler(self):
        self.binary.seek(0)
        return self.binary

    def get_file_handler(self, encoding):
        return TextIOWrapper(self.binary, encoding=encoding)
