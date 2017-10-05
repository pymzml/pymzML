#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface for mzML files

@author: Manuel Koesters
"""
from __future__ import print_function
from pymzml.file_classes import indexedGzip
from pymzml.file_classes import standardGzip
from pymzml.file_classes import standardMzml
from pymzml.utils import GSGR


class FileInterface(object):
    """Interface to different mzML formats."""

    def __init__(self, path, encoding):
        """
        Initialize a object interface to mzML files.

        Arguments:
            path (str)               : path to the mzML file
            encoding (str)           : encoding of the file

        """
        self.encoding     = encoding
        self.file_handler = self._open(path)
        self.offset_dict  = self.file_handler.offset_dict

    def close(self):
        """Close the internal file handler."""
        self.file_handler.close()

    def _open(self, path):
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
        if path.endswith('.gz'):
            if self._indexed_gzip(path):
                file_handler = indexedGzip.IndexedGzip(
                    path,
                    self.encoding
                )
            else:
                file_handler = standardGzip.StandardGzip(
                    path,
                    self.encoding
                )
        else:
            file_handler = standardMzml.StandardMzml(
                path,
                self.encoding
            )
        return file_handler

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

if __name__ == '__main__':
    print(__doc__)
