import unittest
import struct
import math

try:
    import numpy as np
except:
    np = None

import pynumpress


@unittest.skipIf(np is None, "Numpy is required for this test.")
class test_MSNumpress(unittest.TestCase):

    """
    unittest for MSNumpress en- and decoding
    """

    def setUp(self):
        """
        """
        self.mz_data = np.asarray([100.1, 100.01, 100.001, 100.0001], dtype=np.float64)
        self.i_data = np.array([5e6, 6.5e5, 2e6, 12e6])
        self.i_slof_data = np.array([1.0, 2.0, 4.0])
        self.integer = 23
        # self._encoded_int = bytes([ 0x06, 0x07, 0x01 ])
        # pynumpress = MSNumpress([])
        self.fixed_point = 10000

    def test_encode_slof(self):
        fp = pynumpress.optimal_slof_fixed_point(self.i_slof_data)
        encoded_array = pynumpress.encode_slof(
            np.asarray(self.i_slof_data, dtype=np.float64), fp
        )

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
        # pynumpress.encoded_data = test_array
        decoded_array = pynumpress.decode_slof(test_array)
        for i, dec in enumerate(decoded_array):
            self.assertAlmostEqual(dec, self.i_slof_data[i], places=2)
        # self.assertCountEqual(decoded_array, self.i_slof_data)

    def test_encode_decode_slof(self):
        """
        """
        # pynumpress.decoded_data = self.i_slof_data
        print(self.i_slof_data)
        fp = pynumpress.optimal_slof_fixed_point(self.i_slof_data)
        encoded_array = pynumpress.encode_slof(
            np.asarray(self.i_slof_data, dtype=np.float64), fp
        )
        decoded_array = pynumpress.decode_slof(encoded_array)
        for i, dec in enumerate(decoded_array):
            self.assertAlmostEqual(dec, self.i_slof_data[i], places=2)

    def test_encode_pic_i_data(self):
        encoded_array = pynumpress.encode_pic(np.asarray(self.i_data, dtype=np.float64))

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
        decoded_array = pynumpress.decode_pic(test_array)
        self.assertCountEqual(
            decoded_array,
            self.i_data,
            msg="{}\n{}".format([x for x in decoded_array], [x for x in self.i_data]),
        )

    def test_encode_decode_pic(self):
        """
        """
        encoded_array = pynumpress.encode_pic(
            np.asarray(self.i_slof_data, dtype=np.float64)
        )
        decoded_array = pynumpress.decode_pic(encoded_array)
        self.assertCountEqual(self.i_slof_data, decoded_array)

    def test_encode_linear(self):
        decoded_data = self.mz_data
        fp = pynumpress.optimal_linear_fixed_point(self.mz_data)
        encoded_array = pynumpress.encode_linear(decoded_data, fp)
        self.assertEqual(
            len(encoded_array),
            23,
            msg="{0}\n{1}".format(
                [hex(x) for x in encoded_array],
                [
                    "0x41",
                    "0x74",
                    "0x75",
                    "0xa4",
                    "0x70",
                    "0x0",
                    "0x0",
                    "0x0",
                    "0xf6",
                    "0xff",
                    "0xff",
                    "0x7f",
                    "0xc2",
                    "0x89",
                    "0xe2",
                    "0x7f",
                    "0x2b",
                    "0xf3",
                    "0x8a",
                    "0x13",
                    "0xdc",
                    "0x6a",
                    "0x20",
                ],
            ),
        )

        # assert first value
        self.assertEqual(
            0xFF & encoded_array[8],
            0xF6,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                8, hex(0xFF & encoded_array[8]), hex(0xF6)
            ),
        )

        self.assertEqual(
            0xFF & encoded_array[9],
            0xFF,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                9, hex(0xFF & encoded_array[9]), hex(0xFF)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[10],
            0xFF,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                10, hex(0xFF & encoded_array[10]), hex(0xFF)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[11],
            0x7F,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                11, hex(0xFF & encoded_array[11]), hex(0x7F)
            ),
        )

        # assert second value
        self.assertEqual(
            0xFF & encoded_array[12],
            0xC2,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                12, hex(0xFF & encoded_array[12]), hex(0xC2)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[13],
            0x89,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                13, hex(0xFF & encoded_array[13]), hex(0x89)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[14],
            0xE2,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                14, hex(0xFF & encoded_array[14]), hex(0xE2)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[15],
            0x7F,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                15, hex(0xFF & encoded_array[15]), hex(0x7F)
            ),
        )

        # assert third value
        self.assertEqual(
            0xFF & encoded_array[16],
            0x2B,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                16, hex(0xFF & encoded_array[16]), hex(0x2B)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[17],
            0xF3,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                17, hex(0xFF & encoded_array[17]), hex(0xC2)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[18],
            0x8A,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                18, hex(0xFF & encoded_array[18]), hex(0x8A)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[19],
            0x13,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                19, hex(0xFF & encoded_array[19]), hex(0x13)
            ),
        )

        # assert fourth value
        self.assertEqual(
            0xFF & encoded_array[20],
            0xDC,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                19, hex(0xFF & encoded_array[20]), hex(0xDC)
            ),
        )
        self.assertEqual(
            0xFF & encoded_array[21],
            0x6A,
            msg="Fail in value at pos {0}: {1} != {2}".format(
                19, hex(0xFF & encoded_array[21]), hex(0x6A)
            ),
        )
        # self.assertEqual(
        #     0xff & encoded_array[22],
        #     0x20,
        #     msg='Fail in value at pos {0}: {1} != {2}'.format(
        #         19,
        #         hex(0xff & encoded_array[22]),
        #         hex(0x20)
        #     )
        # )

    def test_decode_linear(self):

        # ouput of  >>> PyMSNumpress.encode_linear(self.mz_data, enc,
        # self.fixed_point)
        encoded_array = [
            65,
            116,
            117,
            164,
            112,
            0,
            0,
            0,
            246,
            255,
            255,
            127,
            194,
            137,
            226,
            127,
            43,
            243,
            138,
            19,
            220,
            106,
            32,
        ]

        # make bytearray from hex vals
        encoded_array = np.array(encoded_array, dtype=np.dtype("B"))

        # decode bytearray to numpy array
        decoded_array = pynumpress.decode_linear(encoded_array)
        self.assertIsInstance(decoded_array, np.ndarray)
        self.assertEqual(len(decoded_array), len(self.mz_data))
        for i in range(len(decoded_array)):
            self.assertAlmostEqual(decoded_array[i], self.mz_data[i], places=i + 1)

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
        test_array = np.asarray(test_array, dtype=np.float64)
        fp = pynumpress.optimal_linear_fixed_point(test_array)
        encoded_array = pynumpress.encode_linear(test_array, fp)
        decoded_array = pynumpress.decode_linear(encoded_array)
        for i in range(len(decoded_array)):
            self.assertAlmostEqual(
                decoded_array[i],
                test_array[i],
                places=4,
                msg="error at pos {0}".format(i),
            )

    def test_encode_decode_self_mz(self):
        mz_data = np.asarray(self.mz_data, dtype=np.float64)
        fp = pynumpress.optimal_linear_fixed_point(mz_data)
        encoded_mz_data = pynumpress.encode_linear(mz_data, fp)
        decoded_mz_data = pynumpress.decode_linear(encoded_mz_data)
        for i in range(len(decoded_mz_data)):
            self.assertAlmostEqual(
                decoded_mz_data[i],
                mz_data[i],
                places=4,
                msg="error at pos {0}".format(i),
            )


if __name__ == "__main__":
    unittest.main(verbosity=3)
