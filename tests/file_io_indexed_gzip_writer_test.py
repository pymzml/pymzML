#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Part of pymzml test cases
"""
import os
from pymzml.utils.GSGW import GSGW
import unittest
import zlib
import struct


class GSGWTest(unittest.TestCase):
    """
    TODO: Write messages for assertions
    """

    def setUp(self):
        self.paths = [os.path.join(os.path.dirname(__file__), "data", "unittest.mzml")]
        self.Writer = GSGW(
            self.paths[0],
            max_idx=80,
            max_idx_len=8,
            max_offset_len=8,
            output_path=os.path.abspath(
                os.path.join(".", "tests", "data", "unittest.mzml")
            ),
        )

    def tearDown(self):
        """
        """
        self.Writer.close()
        os.remove(os.path.abspath(os.path.join(".", "tests", "data", "unittest.mzml")))

    def test_init(self):
        self.assertEqual(self.Writer.crc32, 0)
        self.assertEqual(self.Writer.crc32, 0)
        self.assertEqual(
            self.Writer.file_name,
            os.path.abspath(
                os.path.join(
                    # os.path.dirname(__file__),
                    # 'Test',
                    "tests",
                    "data",
                    "unittest.mzml",
                )
            ),
        )

    def test_write_gen_header_index(self):
        self.Writer._write_gen_header(Index=True)
        self.Writer.close()
        file = open(self.paths[0], "rb")
        header = file.read()
        file.close()

        # Normal stuff
        self.assertEqual(header[:2], b"\x1f\x8b")  # Gzip magic bytes
        self.assertEqual(header[2], 8)  # comp
        self.assertEqual(header[3], 16)  # comment flags set
        # self.assertEqual(header[5:9], b'') # time, how to check?
        self.assertEqual(header[8], 2)  # xfl
        self.assertEqual(header[9], 3)  # os

        # extra field with index
        self.assertEqual(header[10:12], b"FU")  # magic index bytes
        self.assertEqual(header[12], 1)  # version

    def test_write_gen_header_no_index(self):
        self.Writer._write_gen_header(Index=False)
        self.Writer.close()
        file = open(self.paths[0], "rb")
        header = file.read()
        file.close()
        # Normal stuff
        self.assertEqual(header[:2], b"\x1f\x8b")
        self.assertEqual(header[2], 8)  # comp
        self.assertEqual(header[3], 0)  # comment flags set
        # self.assertEqual(header[5:9], b'') # time, how to check?
        self.assertEqual(header[8], 2)  # xfl
        self.assertEqual(header[9], 3)  # os
        self.assertEqual(len(header), 10)

    def test_allocate_index_bytes(self):
        self.Writer._allocate_index_bytes()
        self.Writer.close()
        file = open(self.paths[0], "rb")
        data = file.read()
        print(data, data[1], len(data))
        file.close()
        max_idx_num = 80
        max_idx = 8
        max_offset = 8
        self.assertEqual(len(data), ((max_idx + max_offset) * max_idx_num) + 1)

        self.assertEqual(len(data), max_idx_num * (max_idx + max_offset) + 1)

    def test_write_data(self):
        test_string = b"AAAAAAAAbbbbbbbbCCCCCCCC"
        self.Writer._write_data(test_string)
        self.Writer.close()
        Decomp = zlib.decompressobj(-zlib.MAX_WBITS)
        file = open(
            os.path.join(os.path.dirname(__file__), "data", "unittest.mzml"), "rb"
        )
        data = file.read()
        file.close()
        compData = data[:-8]
        crc = struct.unpack("<L", data[-8:-4])[0]
        isize = struct.unpack("<L", data[-4:])[0]
        self.assertEqual(Decomp.decompress(compData), test_string)
        self.assertEqual(crc, zlib.crc32(test_string))
        self.assertEqual(isize, len(test_string) % 2 ** 32)

    def test_add_data(self):
        test_string = b"AAAAAAAAbbbbbbbbCCCCCCCCdddddddd"
        self.Writer.add_data(test_string, 1)
        self.Writer.close()
        file = open(self.paths[0], "rb")
        data = file.read()
        file.close()
        index = self.Writer.index
        self.assertIn(1, index)
        test_file = os.path.join(
            os.path.dirname(__file__),
            "data",
            "uncompressed",
            "CF_07062012_pH8_2_3A.mzML",
        )
        self.Writer = GSGW(test_file, max_idx=80, max_idx_len=8, max_offset_len=8)
        self.Writer.add_data(test_string, "a")
        self.Writer.close()
        file = open(self.paths[0], "rb")
        data = file.read()
        file.close()
        index = self.Writer.index
        self.assertIn("a", index)

    def test_write_index(self):
        test_string = b"AAAAAAAAbbbbbbbbCCCCCCCCdddddddd"

        # with int as id
        # TODO assertions
        self.Writer.add_data(test_string, 1)
        self.Writer.write_index()
        self.Writer.close()
        file = open(self.paths[0], "rb")
        data = file.read()
        file.close()
        index = data[
            15 : 15 + (80 * 16) + 1
        ]  # dont read header (first 15 bytes) and read idx_num * (idx_len + offset_len bytes) and zero termination
        identifier = index[:8].decode("latin-1")
        offset = index[8:16].decode("latin-1")
        self.assertEqual(identifier.strip("\xAC"), "1")
        self.assertIsInstance(offset.strip("\xAC"), str)


if __name__ == "__main__":
    unittest.main(verbosity=3)
