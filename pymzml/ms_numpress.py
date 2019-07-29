#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
MSNumpress decoder class


Authors:

Manuel Kösters
Christian Fufezan
"""
import sys
import struct
import math

import numpy as np


class MSNumpress:
    """
    The library provides implementations of 4 different algorithms,
    1 designed to compress first order smooth data like retention time or M/Z
    arrays, 1 designed to transform first order smooth data for more efficient
    zlib compression, and 2 for compressing non-smooth data with lower
    requirements on precision like ion count arrays.


    ..Note::
        This is a Python implementation of the Golomb-Rice encoding,
        also known as MS-Numpress. As such it is considerably slower than
        the C implementation, which we wrapped into cython. Please make
        yourself a favor and use the the wrapper/c implementation and only
        as a last result this Python implementation.

    """

    def __init__(self, data=None):
        """
        Initialize stateful Numpress De- and Encoding.

        Args:
            array (list): data array with compressed or decompressed data
        """
        self.is_little_endian = True if sys.byteorder == "little" else False
        self.Filler = {
            8: "00000000",
            7: "0000000",
            6: "000000",
            5: "00000",
            4: "0000",
            3: "000",
            2: "00",
            1: "0",
            0: "",
            9: "f",
            10: "ff",
            11: "fff",
            12: "ffff",
            13: "fffff",
            14: "ffffff",
            15: "fffffff",
        }
        # call check what data was set ...
        self._encoded_data = None
        self._decoded_data = None

        if type(data) == bytearray:
            # set data is encoded
            self.data_state = "encoded"
            self._encoded_data = data
        elif type(data) == list:
            # set data is decoded
            self.data_state = "decoded"
            self._decoded_data = data
        else:
            pass

    @property
    def decoded_data(self):
        if self._decoded_data is None:
            raise Exception("decoded data is not set")
        return self._decoded_data

    @decoded_data.setter
    def decoded_data(self, data):
        if type(data) is not list and type(data) is not np.ndarray:
            raise Exception("data must be list")
        self._decoded_data = data

    @property
    def encoded_data(self):
        if self._encoded_data is None:
            raise Exception("encoded data is not set")
        return self._encoded_data

    @encoded_data.setter
    def encoded_data(self, data):
        """Set the data."""
        if type(data) is not bytearray:
            raise Exception("data must be bytearray")
        self._encoded_data = data

    def _linear_fixed_point(self):
        """
        Calculate the optimal predictor coefficient for linear prediction model
        for the Numpress Linear algorithm.

        Returns:
            fixed_point(int): scaling factor for linear prediction
        """
        data = self.decoded_data
        data_size = len(data)
        if data_size == 0:
            return 0
        if data_size == 1:
            return math.floor(0xFFFFFFFF) / data[0]
        max_double = max(data[:2])
        for i in range(2, data_size):
            extrapol = data[i - 1] + (data[i - 1] - data[i - 2])
            diff = data[i] - extrapol
            max_double = max([max_double, math.ceil(abs(diff) + 1)])
        return math.floor(0x7FFFFFFF / max_double)

    def _slof_fixed_point(self):
        """
        Calculate the optimal predictor coefficient for linear prediction model
        for the Numpress Slof algorithm.

        Returns:
            fixed_point(int): scaling factor for linear prediction
        """
        data = self.decoded_data
        if len(data) == 0:
            return 0
        max_double = 1
        for i in range(len(data)):
            x = math.log(data[i] + 1)
            max_double = max([max_double, x])
        fp = math.floor(0xFFFF / max_double)
        return fp

    def _encodeInt(self, integer):
        """
        # RENAME FUNCTION :)
        Encode a given 4 byte integer by truncating leading 1s and 0s
        and saving them in a halfbyte along with the original data

        Args:
            integer (int): Value to be compressed

        Returns:
            bytes (bytearray): encoded bytes
        """
        mask = 0xF0000000

        try:
            integer_as_bytes = struct.pack(">i", integer)
        except:
            integer_as_bytes = None
        init = integer & 0xF0000000
        results = bytearray()

        if integer_as_bytes == b"\x00\x00\x00\x00":
            results.append(0x8)
            x = 8

        elif init == 0:
            x = 0
            for b in integer_as_bytes:
                first_half_byte = (0xFF & b) >> 4
                second_half_byte = 0xF & b
                if first_half_byte == 0:
                    x += 1
                    if second_half_byte == 0:
                        x += 1
                        continue
                    else:
                        results.append(x)
                        break
                else:
                    results.append(x)
                    break

        else:
            for x in range(8):
                m = mask >> 4 * x
                if integer & m == m:
                    continue
                else:
                    results.append(x + 8)
                    break
            if len(results) == 0:
                results.append(x + 8)

        if x < 8:
            for m in range(8 - x):
                r_to_l_mask = 0xF
                np_byte = (integer >> 4 * m) & r_to_l_mask
                results.append(np_byte)

        return results

    def _decodeInt(self, encodedInt):
        """
        Decode an integer from bytes encoded by :py:func:`_encodeInt`

        Args:
            encodedInt (bytearray): encoded bytes

        Returns:
            result (int): decoded form of the encoded integer
        """
        hex_string = ""
        fill = "0"
        for pos, byte in enumerate(encodedInt):
            if pos == 0:
                leading = byte & 0xF
                if leading > 8:
                    leading -= 8
                    fill = "f"
            else:
                hex_string = str(hex(byte))[2:] + hex_string
        hex_string = fill * leading + hex_string
        x = int(hex_string, 16)
        if x > 0x7FFFFFFF:
            x -= 0x100000000

        return x

    def encode_linear(self):
        """
        Use Linear prediction and Golomb coding to compress an array
        of mz values.

        Returns:
            result (bytearray): Golomb encoded bytearray

        EXPAMPLE

        IN:
            [ 12.23123, 14.21431, 23.22222 ]
        OUT:
            (b'\x50\x0c\x0f\x08\x51\x02\x03\x01\x23\x00') <class 'bytearray'>
        """

        ints = [0 for x in range(3)]
        data = self.decoded_data
        fp = self._linear_fixed_point()

        encoded_fixed_point = self._encode_fixed_point(fp)
        result = bytearray(encoded_fixed_point)
        if len(data) == 0:
            return 8

        ints[1] = int(round(data[0] * fp))

        for i in range(4):
            result.append((ints[1] >> (i * 8)) & 0xFF)

        if len(data) == 1:
            return 12

        ints[2] = int(round(data[1] * fp))

        for i in range(4):
            result.append((ints[2] >> (i * 8)) & 0xFF)

        enc_diff = bytearray()
        for i in range(2, len(data)):
            ints[0] = ints[1]
            ints[1] = ints[2]
            ints[2] = int(round(data[i] * fp))
            extrapol = ints[1] + (ints[1] - ints[0])

            diff = ints[2] - extrapol
            enc_diff += self._encodeInt(diff)
            for i in range(1, len(enc_diff), 2):
                final_byte = enc_diff[i] & 0xF | enc_diff[i - 1] << 4
                result.append(final_byte)
            if len(enc_diff) % 2 != 0:
                enc_diff = bytearray([enc_diff[-1]])
            else:
                enc_diff = bytearray()

        self.encoded_data = result
        return result

    def decode_linear(self):
        """
        Decode a Golomb encoded bytearray to its corresponding numpy array.

        Returns:
            result (np.ndarray): NumLin decoded numpy array of the
                original data

        """
        ints = [0 for x in range(3)]
        data = self.encoded_data

        if len(data) < 8:
            raise Exception("Corrupt input data.\nnot enough bytes to read fixed point")

        enc_fp = data
        fp = self._decode_fixed_point(enc_fp)

        if len(data) < 12:
            raise Exception("Corrupt input data.\nnot enough bytes to read first value")

        for i in range(4):
            ints[1] = ints[1] | ((0xFF & (data[8 + i])) << (i * 8))
        i1 = ints[1] / fp

        if len(data) < 16:
            raise Exception("Corrupt input data\nnot enough bytes to read second value")

        for i in range(4):
            ints[2] = ints[2] | ((0xFF & (data[12 + i])) << (i * 8))
        i2 = ints[2] / fp

        diff_vals = self._decode_ints_from_bytearray(16, fp)
        result = [0 for x in range(len(diff_vals) + 2)]
        result[0] = i1
        result[1] = i2
        i = 2
        for diff in diff_vals:
            ints[0] = ints[1]
            ints[1] = ints[2]
            ints[2] = diff
            extrapol = ints[1] + (ints[1] - ints[0])
            val = extrapol + ints[2]
            result[i] = val / fp
            ints[2] = val
            i += 1

        return result

    def _decode_ints_from_bytearray(self, pos, normalization=1):
        """
        Decode truncated integer encoded values and end position
        in bytearray.

        Args:
            pos (int) : start position in array

        Returns:
            results (list): ...
        """
        # results = np.empty(len(self.encoded_data) * 2)
        results = [0 for x in range(len(self.encoded_data) * 2)]
        leading_count = None
        i = 0
        while pos < len(self.encoded_data):
            current_byte = "{0:02x}".format(self.encoded_data[pos])
            for byte_pos in [0, 1]:
                hb = current_byte[byte_pos]
                if leading_count is None:
                    if hb == "8":
                        results[i] = 0
                        i += 1
                    else:
                        leading_count = int(hb, 16)
                        hex_str = ""
                        cb = leading_count - (8 * math.floor(leading_count / 8))
                else:
                    hex_str = "{0}{1}".format(hb, hex_str)
                    cb += 1
                    try:
                        1 / (cb - 8)
                    except:
                        final_int = int(self.Filler[leading_count] + hex_str, 16)
                        if final_int > 0x7FFFFFFF:
                            final_int -= 0x100000000
                        results[i] = final_int
                        i += 1
                        leading_count = None
            pos += 1
        return results[:i]

    def encode_pic(self):
        """
        Encode Ion count data by rounding to the next integer and
        store in a truncated form.

        Returns:
            result (bytearray): array with rounded
                ion count data in bytes
        """
        # need to be optimized
        res = bytearray()
        final = bytearray()

        for val in self.decoded_data:
            val = int(round(val))  # simply round
            enc_int = self._encodeInt(val)
            res.extend(enc_int)

        # assure res has an even length
        if len(res) % 2 != 0:
            res.append(0)

        # pull halfbytes together
        for i in range(1, len(res), 2):
            val = (res[i - 1] << 4) | res[i] & 0xF
            final.append(val)

        self.encoded_data = final
        return final

    def decode_pic(self):
        """
        Decode ion count data compressed with :py:func:`encodePic`

        Returns:
            result (array): decoded Ion count data as numpy array
        """
        results = []
        data = self.encoded_data
        read_first = True
        hb_to_read = 0
        current_value = bytearray()

        # TODO fix problem when 2 or more zeroes appear after each other
        # => if first hbc is 8, the next number is a hbc again and not data

        for val in data:
            if hb_to_read == 0:
                if read_first is True:
                    current_value = bytearray()
                    count = (0xFF & val) >> 4
                    current_value.append(count)
                    hb_to_read = 8 - count
                    read_first = False
                else:
                    current_value = bytearray()
                    count = 0xF & val
                    current_value.append(count)
                    hb_to_read = 8 - count
                    read_first = True
            if hb_to_read != 0:
                if hb_to_read == 1:
                    if read_first is True:
                        hb = (0xFF & val) >> 4
                        current_value.append(hb)
                        hb_to_read -= 1
                        dec_int = self._decodeInt(current_value)
                        current_value = bytearray()
                        results.append(dec_int)
                        count = 0xF & val
                        current_value.append(count)
                        hb_to_read = 8 - count
                        continue
                    else:
                        hb = 0xF & val
                        current_value.append(hb)
                        hb_to_read -= 1
                        dec_int = self._decodeInt(current_value)
                        current_value = bytearray()
                        results.append(dec_int)
                        read_first = True
                        continue
                if read_first is True:
                    hb1 = (0xFF & val) >> 4
                    hb2 = 0xF & val
                    current_value.append(hb1)
                    current_value.append(hb2)
                    hb_to_read -= 2
                    if hb_to_read == 0:
                        dec_int = self._decodeInt(current_value)
                        results.append(dec_int)
                        current_value = bytearray()
                        continue
                else:
                    hb = 0xF & val
                    current_value.append(hb)
                    read_first = True
                    hb_to_read -= 1

        self.decoded_data = results

        return results

    def encode_slof(self):
        """
        encode ion count data by multiplying the logarithm of each value with
        a scaling factor, rounding to nearest integer, and saving the 2 LSB.

        Returns:
            result (bytearray): short logged float compressed bytearray
        """
        data = self.decoded_data
        self.fixed_point = self._slof_fixed_point()
        res = self._encode_fixed_point(self.fixed_point)
        for i in range(len(data)):
            x = math.floor((math.log(data[i] + 1)) * self.fixed_point + 0.5)
            res.append(0xFF & x)
            res.append(x >> 8)
        self.encoded_data = res
        return res

    def decode_slof(self):
        """
        Decode short logged float compressed data.

        Returns:
            result (bytearray): array with decoded ion count data
        """
        data = self.encoded_data
        if len(data) < 8:
            return -1
        res = list()
        fixed_point = self._decode_fixed_point(data)

        for i in range(8, len(data), 2):
            x = 0xFF & data[i] | ((0xFF & data[i + 1]) << 8)
            res.append(math.exp((0xFFFF & x) / fixed_point) - 1)

        self.decoded_data = res
        return res

    def encode_safe(self):
        """
        Transform values by linear prediction without scaling or truncated
        representation.

        Returns:
            result (bytearray): transformed data in bytes
        """
        # result = bytearray()
        # assert data format is correct
        # save_first_2_values_unencoded()
        # for val in self.data[2:]:
        #   pred = do_linear_prediction()
        #   enc  = do_Golomb_encoding()
        #   result.extend(enc)
        # return result
        pass

    def decode_safe(self):
        # if not self.data_state == 'decoded':
        #   raise Exception('No encoded data found\nPlease set encoded Data')

        # result = np.ndarray()
        # int1 = read_int1(8)
        # int2 = read_int2(8)
        # add ints to result
        # for x in range(0, len(self.data, 2)):
        #   enc_int = self.data[x:x+8]
        #   result.append(dec_int)
        pass

    def _encode_fixed_point(self, value):
        """
        Save a given float as bytes.

        Args:
            value(float): fixed point
        Returns:
            res (bytearray): encoded fixed point
        """
        res = bytearray(8)
        fp = value
        fp = struct.pack("<d", fp)
        fp = struct.unpack("<q", fp)[0]
        if self.is_little_endian:
            for i in range(8):
                res[7 - i] = (fp >> (8 * i)) & 0xFF
        else:
            for i in range(7, -1, -1):
                res[7 - i] = (fp >> (8 * i)) & 0xFF
        return res

    def _decode_fixed_point(self, value):
        """
        Decode a given bytearray to float.

        Args:
            value(bytearray): encoded fixed point
        Returns:
            res (float): encoded fixed point
        """
        fp = 0
        if self.is_little_endian:
            for i in range(8):
                fp = fp | ((0x00FF & value[7 - i]) << (8 * i))
        else:
            for i in range(7, -1, -1):
                fp = fp | ((0x00FF & value[7 - i]) << (8 * i))
        fp = struct.pack("<q", fp)
        fp = struct.unpack("<d", fp)[0]
        return fp


if __name__ == "__main__":
    print(__doc__)
