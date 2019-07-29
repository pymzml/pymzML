#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
Reader class for indexed gzipped files
"""
import struct
import zlib
from collections import OrderedDict


class GSGR(object):
    """
    Generalized Gzip reader class which enables random access in files
    written with the :class:`~pymzml.utils.GSGW.GSGW` class.

    Keyword Arguments:
        file (str): path to file to read
    """

    def __init__(self, file=None):

        self.file_in = open(file, "rb")
        self.filename = file
        self.magic_bytes = b"\x1f\x8b"
        self.indexed = True

        if not self._check_magic_bytes():
            raise Exception("not a gzip file (wrong magic bytes)")

        self.random_access = False  # initial state, until index is read

        self._read_basic_header()
        if self.flg & 0 != 0:  # FTEXT flag
            self.ascii_file = True
        if self.flg & 2 != 0:  # FHCRC flag
            crc16 = self.file_in.read(2)
        if self.flg & 4 != 0:  # FEXTRA flag
            # TODO: maybe never tested
            xlen = struct.unpack("<H", self.file_in.read(2))[0]
            self.file_in.seek(xlen)
        if self.flg & 8 != 0:  # FNAME flag
            self.fname = self._read_until_zero()
        if self.flg & 16 == 0:  # FCOMMENT flag NOT SET
            self.indexed = False
        else:
            self._read_index()

    def __del__(self):
        try:
            self.close()
        except:
            raise Exception(" cant close file")

    def seek(self, offset):
        """
        Seek to byte offset in input file.

        Arguments:
            offset (int): byte offset to seek to in FileIn

        Returns:
            None
        """
        self.file_in.seek(offset)
        return

    def read_block(self, index):
        """
        Read and return the data block with the unique index `index`

        Arguments:
            index(int or str): identifier associated with a specific block

        Returns:
            data (str): indexed text block as string
        """
        start = self.index[index]
        try:
            end = self.index[int(index) + 1]
        except:
            end = self.file_in.seek(0, 2)
        self.file_in.seek(start)
        readSize = end - start
        comp_data = self.file_in.read(readSize)
        data = zlib.decompress(comp_data, -zlib.MAX_WBITS)
        return data

    def _check_magic_bytes(self):
        """
        Check if file is a gzip file.
        """
        # self.file_in.seek(0) # make sure file pointer is at start
        mb = self.file_in.read(2)
        return mb == self.magic_bytes

    def _read_basic_header(self):
        """
        Read and save compression method, bitflags, changetime,
        compression speed and os.
        """
        self.file_in.seek(2)  # make sure filepoiner is at correct position
        vals = struct.unpack("<BBLBB", self.file_in.read(8))
        self.cm = vals[0]
        self.flg = vals[1]
        self.mtime = vals[2]
        self.xfl = vals[3]
        self.os = vals[4]

    def _read_until_zero(self):
        """
        Read input until \x00 is reached
        """
        buf = b""
        c = self.file_in.read(1)
        while c != b"\x00":
            buf += c
            c = self.file_in.read(1)
        return buf

    def _read_index(self):
        """
        Read and save offset dict from indexed gzip file
        """
        self.index = OrderedDict()
        self.file_in.seek(10)  # make sure file pointer is at right position
        mb = self.file_in.read(3)
        if mb != b"FU\x01":  # All hail MK!
            print("No index in comment field found. No random access possible")
            self.indexed = False
        lengths = struct.unpack("<BB", self.file_in.read(2))
        self.idx_len = lengths[0]
        self.offset_len = lengths[1]
        ID_block = b""
        while b"\x00" not in ID_block:
            ID_block = self.file_in.read(self.idx_len)
            OffsetBlock = self.file_in.read(self.offset_len)
            try:
                try:
                    Identifier = int(ID_block.decode("latin-1").strip("¬"))
                except:
                    Identifier = ID_block.decode("latin-1").strip("¬")
                Offset = int(OffsetBlock.decode("latin-1").strip("¬"))
                self.index[Identifier] = Offset
            except:
                break
        self.file_in.seek(0)

    def read(self, size=-1):
        """
        Read the content of the in File in binary mode

        Keyword Arguments:
            size (int, optional): number of bytes to read, -1 for everything

        Returns:
            data (bytes): parsed bytes from input file
        """
        return self.file_in.read(size)

    def __enter__(self):
        """
        Enable the with syntax for this class (entry point)
        """
        return self.file_in

    def __exit__(self, exc_type, exc_value, traceback):
        """
        destructor when using this class with 'with .. as '
        """
        self.file_in.close()

    def close(self):
        """
        Close the internal Filehandler
        """
        self.file_in.close()


if __name__ == "__main__":
    print(__doc__)
