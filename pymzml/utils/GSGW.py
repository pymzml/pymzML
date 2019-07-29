#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
Writer class for indexed gzipped files
"""
import struct
import time
import zlib
from collections import OrderedDict


class GSGW(object):
    """

    Generalized Gzip writer class with random access to indexed offsets.

    Keyword Arguments:
        file (string)        : Filename for the resulting file
        max_idx (int)        : max number of indices which can be saved in
                                this file
        max_idx_len (int)    : maximal length of the index in bytes, must
                                be between 1 and 255
        max_offset_len (int) : maximal length of the offset in bytes
        output_path (str)    : path to the output file

    """

    def __init__(
        self,
        file=None,
        max_idx=10000,
        max_idx_len=8,
        max_offset_len=8,
        output_path="./test.dat.igzip",
        comp_str=-1,
    ):
        self.Lock = False
        self._format_version = 1  # max 255!!!
        self.file_name = output_path
        self.max_idx_num = max_idx
        self.max_idx_len = max_idx_len
        self.max_offset_len = max_offset_len
        self.generic_header = OrderedDict(
            [
                ("MAGIC_BYTE_1", b"\x1f"),
                ("MAGIC_BYTE_2", b"\x8b"),
                ("COMPRESSION", b"\x08"),
                ("FLAGS", b"\x00"),
                ("DATE", b"\x00\x00\x00\x00"),
                ("XFL", b"\x02"),
                ("OS", b"\x03"),
            ]
        )
        self.index = OrderedDict()
        self.first_header_set = False
        self._file_out = None
        self._encoding = "latin-1"
        # magic bytes. FU+version
        self.index_magic_bytes = b"FU" + struct.pack("<B", self._format_version)
        self.crc32 = 0
        self.isize = 0
        self.comp_str = comp_str

    def __del__(self):
        """
        Close the file object properly after this object is deleted
        """
        self.file_out.close()

    def close(self):
        """
        Close the internal file object.
        """
        self.file_out.close()

    @property
    def file_out(self):
        """
        Output filehandler
        """
        if self._file_out is None:
            self._file_out = open(self.file_name, "wb")
        return self._file_out

    @property
    def encoding(self):
        """
        Returns the encoding used for this file
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Set the file encoding for the output file.
        """
        assert type(encoding) == str, "encoding must be a string"
        self._encoding = encoding

    def _write_gen_header(self, Index=False, FLAGS=None):
        """
        Write a valid gzip header with creation time, user defined flag fields
        and allocated index.

        Keyword Arguments:
            Index (bool)           : whether to or not to write an
                                        index into this header.
            FLAGS (list, optional) : list of flags (FTEXT, FHCRC, FEXTRA,
                                        FNAME) to set for this header.

        Returns:
            offset (int): byte offset of the file pointer
        """
        if FLAGS is None:
            FLAGS = []
        FTEXT, FHCRC, FEXTRA, FNAME = 1, 2, 4, 8  # extra field bit flags
        current_time = int(time.time())
        time_byte = struct.pack("<L", current_time)
        self.generic_header["DATE"] = time_byte
        if Index:
            self.generic_header["FLAGS"] = b"\x10"
        if FLAGS is not None:
            if "FTEXT" in FLAGS:
                self.generic_header["FLAGS"] = self.generic_header["FLAGS"] & FTEXT

            if "FHCRC" in FLAGS:
                header_crc32 = 0
                self.generic_header["FLAGS"] = self.generic_header["FLAGS"] & FHCRC
                for byte in self.generic_header.values():
                    header_crc32 = zlib.crc32(byte, header_crc32)

            if "FEXTRA" in FLAGS:
                self.generic_header["FLAGS"] = self.generic_header["FLAGS"] & FEXTRA

            if "FNAME" in FLAGS:
                self.generic_header["FLAGS"] = self.generic_header["FLAGS"] & FNAME

        for value in self.generic_header.values():
            self.file_out.write(value)
        if "FEXTRA" in FLAGS:
            # WRITE EXTRA FIELD
            pass

        if "FNAME" in FLAGS:
            # WRITE FNAME FIELD
            fName = self.file_name.split("/")[-1]

        if Index:
            self.generic_header["FLAGS"] = b"\x00"
            self.file_out.write(self.index_magic_bytes)
            self.file_out.write(struct.pack("<B", self.max_idx_len))
            self.file_out.write(struct.pack("<B", self.max_offset_len))
            self.index_offset = self.file_out.tell()
            self._allocate_index_bytes()

        if "FHCRC" in FLAGS:
            # WRITE checksum for header
            pass

        return self.file_out.tell()

    def _allocate_index_bytes(self):
        """
        Allocate 'self.max_index_num' bytes of length 'self.max_idx_len'
        in the header for inserting the index later on.
        """
        id_placeholder = self.max_idx_len * b"\x01"
        offset_placeholder = self.max_offset_len * b"\x01"
        for i in range(self.max_idx_num):
            self.file_out.write(id_placeholder)
            self.file_out.write(offset_placeholder)
        self.file_out.write(b"\x00")
        return

    def _write_data(self, data):
        """
        Write data into file-stream.

        Arguments:
            data (str): uncompressed data
        """
        Compressor = zlib.compressobj(
            self.comp_str, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0
        )
        # compress data and flush (includes writing crc32 and isize)
        if isinstance(data, bytes) is False:
            data = bytes(data, "latin-1")
        self.crc32 = zlib.crc32(data)
        self.isize = len(data) % 2 ** 32
        comp_data = Compressor.compress(data) + Compressor.flush()
        self.file_out.write(comp_data)
        self.file_out.write(struct.pack("<L", self.crc32))
        self.file_out.write(struct.pack("<L", self.isize))
        return

    def add_data(self, data, identifier):
        """
        Create a new gzip member with compressed 'data' indexed with 'index'.

        Arguments:
            data (str)         : uncompressed data to write to file
            index (str or int) : unique index for the data
        """
        if self.Lock is False:
            if len(self.index) + 1 > self.max_idx_num:
                print(
                    """
    WARNING: Reached maximum number of indexed data blocks
    '({0}), cannot add any more data!
                    """.format(
                        self.max_idx_num
                    )
                )
                return False

            if not self.first_header_set:
                self._write_gen_header(Index=True)
                self.first_header_set = True
            else:
                # do we need this?
                self._write_gen_header(Index=False)

            self.index[identifier] = self.file_out.tell()
            self._write_data(data)
            return
        else:
            raise Exception("Cant add any more data if index is already written")

    def _write_identifier(self, identifier):
        """
        Convert and write the identifier into output file.

        Arguments:
            identifier (str or int): identifier to write into index
        """
        id_format = "{0:\xAC>" + str(self.max_idx_len) + "}"
        identifier = str(identifier)
        identifier = id_format.format(identifier).encode("latin-1")
        self.file_out.write(identifier)
        return

    def _write_offset(self, offset):
        """
        Convert and write offset to output file.

        Arguments:
            offset (int): offset which will be formatted and written
                into file index
        """
        offset_format = "{0:\xAC>" + str(self.max_offset_len) + "}"
        offset = str(offset)
        offset = offset_format.format(offset).encode("latin-1")
        self.file_out.write(offset)
        return

    def write_index(self):
        """
        Only called after all the data is written, i.e. all calls to
        :func:`~GSGW.add_data` have been done.

        Seek back to the beginning of the file and write the index into the
        allocated comment bytes (see _write_gen_header(Index=True)).
        """
        self.Lock = True
        self.file_out.seek(self.index_offset)
        for identifier, offset in self.index.items():
            self._write_identifier(identifier)
            self._write_offset(offset)

    def __enter__(self):
        """
        Enable the with syntax for this class (entry point).
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Destructor when using this class with 'with .. as'."""
        self.file_out.close()


if __name__ == "__main__":
    print(__doc__)
