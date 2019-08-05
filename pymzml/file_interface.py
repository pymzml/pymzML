#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for mzML files

@author: Manuel Koesters
"""
from io import BytesIO
from pymzml.file_classes import indexedGzip, standardGzip, standardMzml, bytesMzml
from pymzml.utils import GSGR


class FileInterface(object):
    """Interface to different mzML formats."""

    def __init__(self, path, encoding, build_index_from_scratch=False):
        """
        Initialize a object interface to mzML files.

        Arguments:
            path (str)               : path to the mzML file
            encoding (str)           : encoding of the file

        """
        self.build_index_from_scratch = build_index_from_scratch
        self.encoding = encoding
        self.file_handler = self._open(path)
        self.offset_dict = self.file_handler.offset_dict

    def close(self):
        """Close the internal file handler."""
        self.file_handler.close()

    def _open(self, path_or_file):
        """
        Open a file like object resp. a wrapper for a file like object.

        Arguments:
            path (str): path to the mzml file

        Returns:
            file_handler: instance of
            :py:class:`~pymzml.file_classes.standardGzip.StandardGzip`,
            :py:class:`~pymzml.file_classes.indexedGzip.IndexedGzip` or
            :py:class:`~pymzml.file_classes.standardMzml.StandardMzml`,
            based on the file ending of 'path'
        """
        if isinstance(path_or_file, BytesIO):
            return bytesMzml.BytesMzml(
                path_or_file, self.encoding, self.build_index_from_scratch
            )
        if path_or_file.endswith(".gz"):
            if self._indexed_gzip(path_or_file):
                return indexedGzip.IndexedGzip(path_or_file, self.encoding)
            else:
                return standardGzip.StandardGzip(path_or_file, self.encoding)
        return standardMzml.StandardMzml(
            path_or_file, self.encoding, self.build_index_from_scratch
        )

    def _indexed_gzip(self, path):
        """
        Check if the given file is an indexed gzip file or not.

        Arguments:
            path (str): path to the file

        Returns:
            bool : `True` if path is a gzip file with index, else `False`
        """
        indexed = False
        indexed = GSGR.GSGR(path).indexed
        return indexed

    def read(self, size=-1):
        """
        Read binary data from file handler.

        Keyword Arguments:
            size (int): Number of bytes to read from file, -1 to
            read to end of file

        Returns:
            data (str): byte string with defined size of the input data
        """
        return self.file_handler.read(size)

    def __getitem__(self, identifier):
        """
        Access the item with id 'identifier' in the file.

        Arguments:
            identifier (str): native id of the item to access

        Returns:
            data (str): text associated with the given identifier
        """
        # if type(self.offset_dict) == dict:
        #     self.offset_dict.update(self.file_handler.offset_dict)
        return self.file_handler[identifier]


if __name__ == "__main__":
    print(__doc__)
