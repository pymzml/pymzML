import unittest
import struct
import math

try:
    import numpy as np
except:
    np = None

from pymzml.ms_numpress import MSNumpress


@unittest.skipIf(np is None, "Numpy is required for this test.")
class test_MSNumpress(unittest.TestCase):

    """
    unittest for MSNumpress en- and decoding
    """

    def setUp(self):
        """
        """
        self.mz_data = np.asarray([100.1, 100.01, 100.001, 100.0001], dtype=np.float64)
        self.i_data = [5e6, 6.5e5, 2e6, 12e6]
        self.i_slof_data = [1, 2, 4]
        self.integer = 23
        # self._encoded_int = bytes([ 0x06, 0x07, 0x01 ])
        self.Decoder = MSNumpress()
        self.fixed_point = 10000

    def test_enc_int_leading_zeros(self):
        encoded_integer = self.Decoder._encodeInt(1)
        self.assertEqual(encoded_integer[0], 0x07)
        encoded_integer = self.Decoder._encodeInt(16)
        self.assertEqual(encoded_integer[0], 0x06)

    def test_enc_int_leading_ones(self):
        bytearray(b"\x08\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x07")
        encoded_integer = self.Decoder._encodeInt((2 ** 31) - 1)
        self.assertEqual(encoded_integer[0], 0x08)
        self.assertEqual(encoded_integer[1], 0x0F)

    def test_encodeInt_negative(self):
        """
        """
        negative_integer = -1
        encoded_integer = self.Decoder._encodeInt(negative_integer)
        # print('encoded', encoded_integer)
        self.assertEqual(encoded_integer[0], 0xF)
        self.assertEqual(encoded_integer[1], 0xF)

    def test_encodeInt_0(self):
        encoded_integer = self.Decoder._encodeInt(0)
        self.assertEqual(len(encoded_integer), 1, msg="{}".format(encoded_integer))
        self.assertEqual(encoded_integer[0], 0x08)

    def test_encodeInt_256(self):
        encoded_integer = self.Decoder._encodeInt(256)
        self.assertEqual(len(encoded_integer), 4)
        self.assertEqual(encoded_integer[0], 0x05)
        self.assertEqual(encoded_integer[1], 0x00)
        self.assertEqual(encoded_integer[2], 0x00)
        self.assertEqual(encoded_integer[3], 0x01)

    def test_encode_4096(self):
        encoded_integer = self.Decoder._encodeInt(4096)
        self.assertEqual(len(encoded_integer), 5)
        self.assertEqual(encoded_integer[0], 0x04)
        self.assertEqual(encoded_integer[1], 0x00)
        self.assertEqual(encoded_integer[2], 0x00)
        self.assertEqual(encoded_integer[3], 0x00)
        self.assertEqual(encoded_integer[4], 0x01)

    def test_dec_int_leading_zeros(self):
        encoded_integer = bytearray([0x07, 0x01])
        decoded_integer = self.Decoder._decodeInt(encoded_integer)
        self.assertEqual(decoded_integer, 1)

    def test_encode_decode_int(self):
        encoded_integer = self.Decoder._encodeInt(200)
        # print(encoded_integer)
        decoded_integer = self.Decoder._decodeInt(encoded_integer)
        self.assertEqual(decoded_integer, 200)

    def test_dec_int_leading_ones(self):

        encoded_integer = bytearray(b"\x08\n\x03\x04\x01\x05\x03\x07\x07")
        decoded_integer = self.Decoder._decodeInt(encoded_integer)
        # print(decoded_integer)
        self.assertEqual(
            decoded_integer,
            1999967290,
            msg="result: {}\nexpected: {}".format(decoded_integer, hex(1999967290)),
        )

    def test_dec_int_negative(self):
        encoded_negative_int = bytearray([0x0F, 0x0F])
        decoded_negative_int = self.Decoder._decodeInt(encoded_negative_int)
        self.assertEqual(decoded_negative_int, -1)

    def test_encode_slof(self):
        self.Decoder.decoded_data = self.i_slof_data
        encoded_array = self.Decoder.encode_slof()

        self.assertEqual(len(encoded_array), 14)

        self.assertEqual(encoded_array[0], 0x40)
        self.assertEqual(encoded_array[1], 0xE3)
        self.assertEqual(encoded_array[2], 0xE1)
        self.assertEqual(encoded_array[3], 0xE0)
        self.assertEqual(encoded_array[4], 0x0)
        self.assertEqual(encoded_array[5], 0x0)
        self.assertEqual(encoded_array[6], 0x0)
        self.assertEqual(encoded_array[7], 0x0)
        self.assertEqual(encoded_array[8], 0x40)
        self.assertEqual(encoded_array[9], 0x6E)
        self.assertEqual(encoded_array[10], 0xBE)
        self.assertEqual(encoded_array[11], 0xAE)
        self.assertEqual(encoded_array[12], 0xFF)
        self.assertEqual(encoded_array[13], 0xFF)

    def test_decode_slof(self):
        test_array = [
            0x40,
            0xC3,
            0x88,
            0x0,
            0x0,
            0x0,
            0x0,
            0x0,
            0x13,
            0x1B,
            0xEA,
            0x2A,
            0xDE,
            0x3E,
        ]
        test_array = bytearray(test_array)
        self.Decoder.encoded_data = test_array
        decoded_array = self.Decoder.decode_slof()
        for i, dec in enumerate(decoded_array):
            self.assertAlmostEqual(dec, self.i_slof_data[i], places=2)
        # self.assertCountEqual(decoded_array, self.i_slof_data)

    def test_encode_decode_slof(self):
        """
        """
        self.Decoder.decoded_data = self.i_slof_data
        self.Decoder.encode_slof()
        decoded_array = self.Decoder.decode_slof()
        for i, dec in enumerate(decoded_array):
            self.assertAlmostEqual(dec, self.i_slof_data[i], places=2)

    def test_encode_pic_i_data(self):
        self.Decoder.decoded_data = self.i_data
        encoded_array = self.Decoder.encode_pic()

        self.assertEqual(
            len(encoded_array), 14, msg="{}".format([hex(x) for x in encoded_array])
        )

        self.assertEqual(encoded_array[0], 0x20)
        self.assertEqual(encoded_array[1], 0x4B)
        self.assertEqual(encoded_array[2], 0x4C)
        self.assertEqual(encoded_array[3], 0x43)
        self.assertEqual(encoded_array[4], 0x1)
        self.assertEqual(encoded_array[5], 0xBE)
        self.assertEqual(encoded_array[6], 0x92)
        self.assertEqual(encoded_array[7], 0x8)
        self.assertEqual(encoded_array[8], 0x48)
        self.assertEqual(encoded_array[9], 0xE1)
        self.assertEqual(encoded_array[10], 0x20)
        self.assertEqual(encoded_array[11], 0xB)
        self.assertEqual(encoded_array[12], 0x17)
        self.assertEqual(encoded_array[13], 0xB0)

    def test_decode_pic_i_data(self):
        test_array = [
            0x20,
            0x4B,
            0x4C,
            0x43,
            0x1,
            0xBE,
            0x92,
            0x8,
            0x48,
            0xE1,
            0x20,
            0xB,
            0x17,
            0xB0,
        ]
        test_array = bytearray(test_array)
        self.Decoder.encoded_data = test_array
        decoded_array = self.Decoder.decode_pic()
        self.assertCountEqual(
            decoded_array,
            self.i_data,
            msg="{}\n{}".format([x for x in decoded_array], [x for x in self.i_data]),
        )

    def test_encode_decode_pic(self):
        """
        """
        self.Decoder.decoded_data = self.i_slof_data
        self.Decoder.encode_pic()
        decoded_array = self.Decoder.decode_pic()
        self.assertCountEqual(self.i_slof_data, decoded_array)

    def test_encode_decode_fixed_point(self):
        encoded_fixed_point = self.Decoder._encode_fixed_point(self.fixed_point)
        decoded_fixed_point = self.Decoder._decode_fixed_point(encoded_fixed_point)
        self.assertEqual(self.fixed_point, decoded_fixed_point)

    # def test_encode_linear(self):
    #     self.Decoder.decoded_data = self.mz_data
    #     self.Decoder.encoded_data = None
    #     encoded_array = self.Decoder.encode_linear()
    #     self.assertEqual(
    #         len(encoded_array),
    #         23,
    #         msg='{0}\n{1}'.format(
    #             [hex(x) for x in encoded_array],
    #             [
    #                 '0x41', '0x74', '0x75', '0xa4', '0x70', '0x0', '0x0',
    #                 '0x0', '0xf6', '0xff', '0xff', '0x7f', '0xc2', '0x89',
    #                 '0xe2', '0x7f', '0x2b', '0xf3', '0x8a', '0x13', '0xdc',
    #                 '0x6a', '0x20'
    #             ]
    #         )
    #     )

    #     # assert first value
    #     self.assertEqual(
    #         0xff & encoded_array[8],
    #         0xf6,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             8, hex(0xff & encoded_array[8]), hex(0xf6)
    #         )
    #     )

    #     self.assertEqual(
    #         0xff & encoded_array[9],
    #         0xff,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             9,
    #             hex(0xff & encoded_array[9]),
    #             hex(0xff)
    #         )
    #         )
    #     self.assertEqual(
    #         0xff & encoded_array[10],
    #         0xff,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             10,
    #             hex(0xff & encoded_array[10]),
    #             hex(0xff)
    #         )
    #         )
    #     self.assertEqual(
    #         0xff & encoded_array[11],
    #         0x7f,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             11,
    #             hex(0xff & encoded_array[11]),
    #             hex(0x7f)
    #         )
    #         )

    #     # assert second value
    #     self.assertEqual(
    #         0xff & encoded_array[12],
    #         0xc2,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             12,
    #             hex(0xff & encoded_array[12]),
    #             hex(0xc2)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[13],
    #         0x89,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             13,
    #             hex(0xff & encoded_array[13]),
    #             hex(0x89)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[14],
    #         0xe2,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             14,
    #             hex(0xff & encoded_array[14]),
    #             hex(0xe2)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[15],
    #         0x7f,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             15,
    #             hex(0xff & encoded_array[15]),
    #             hex(0x7f)
    #         )
    #     )

    #     # assert third value
    #     self.assertEqual(
    #         0xff & encoded_array[16],
    #         0x2b,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             16,
    #             hex(0xff & encoded_array[16]),
    #             hex(0x2b)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[17],
    #         0xf3,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             17,
    #             hex(0xff & encoded_array[17]),
    #             hex(0xc2)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[18],
    #         0x8a,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             18,
    #             hex(0xff & encoded_array[18]),
    #             hex(0x8a)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[19],
    #         0x13,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             19,
    #             hex(0xff & encoded_array[19]),
    #             hex(0x13)
    #         )
    #     )

    #     # assert fourth value
    #     self.assertEqual(
    #         0xff & encoded_array[20],
    #         0xdc,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             19,
    #             hex(0xff & encoded_array[20]),
    #             hex(0xdc)
    #         )
    #     )
    #     self.assertEqual(
    #         0xff & encoded_array[21],
    #         0x6a,
    #         msg='Fail in value at pos {0}: {1} != {2}'.format(
    #             19,
    #             hex(0xff & encoded_array[21]),
    #             hex(0x6a)
    #         )
    #     )
    #     # self.assertEqual(
    #     #     0xff & encoded_array[22],
    #     #     0x20,
    #     #     msg='Fail in value at pos {0}: {1} != {2}'.format(
    #     #         19,
    #     #         hex(0xff & encoded_array[22]),
    #     #         hex(0x20)
    #     #     )
    #     # )

    # def test_decode_linear(self):

    #     # ouput of  >>> PyMSNumpress.encode_linear(self.mz_data, enc,
    #     # self.fixed_point)
    #     encoded_array = [
    #         65, 116, 117, 164, 112, 0, 0, 0, 246, 255,
    #         255, 127, 194, 137, 226, 127, 43, 243, 138, 19, 220, 106, 32
    #     ]

    #     # make bytearray from hex vals
    #     encoded_array = bytearray(encoded_array)
    #     MSNumpress.encoded_data = encoded_array

    #     # decode bytearray to numpy array
    #     decoded_array = self.Decoder.decode_linear()
    #     self.assertIsInstance(decoded_array, np.ndarray)
    #     self.assertEqual(len(decoded_array), len(self.mz_data))
    #     for i in range(len(decoded_array)):
    #         self.assertAlmostEqual(
    #             decoded_array[i], self.mz_data[i], places=i+1)

    def test_encode_decode_linear(self):
        """
        """
        test_array = [
            100.00066,
            100.00217,
            100.00368,
            100.00519,
            111.73335,
            111.73513,
            111.73692,
            111.7387,
            111.74049,
            111.74227,
            111.74406,
            111.74584,
            111.74763,
            111.74941,
            111.7512,
            111.75298,
            111.75477,
            112.00694,
            112.00873,
            112.01052,
            112.01231,
            112.0141,
            112.01589,
            112.01768,
        ]
        self.Decoder.decoded_data = test_array
        self.Decoder.encode_linear()
        decoded_array = self.Decoder.decode_linear()
        for i in range(len(decoded_array)):
            self.assertAlmostEqual(
                decoded_array[i],
                test_array[i],
                places=4,
                msg="error at pos {0}".format(i),
            )

    def test_encode_decode_self_mz(self):
        self.Decoder.decoded_data = self.mz_data
        self.Decoder.encode_linear()
        decoded_array = self.Decoder.decode_linear()
        for i in range(len(decoded_array)):
            self.assertAlmostEqual(
                decoded_array[i],
                self.mz_data[i],
                places=4,
                msg="error at pos {0}".format(i),
            )


if __name__ == "__main__":
    unittest.main(verbosity=3)
