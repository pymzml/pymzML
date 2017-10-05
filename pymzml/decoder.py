#!/usr/bin/env python3
"""
Classes to encode and decode :py:attr:`~pymzml.spec.Spectrum.mz` and
:py:attr:`~pymzml.spec.Spectrum.i` values.

@author M. Kösters, C. Fufezan
"""
from __future__ import print_function
from multiprocessing import Pool
from base64 import b64decode as b64dec
import zlib
import struct
import pymzml

try:
    import numpy as np
except:
    global np
    np = None


def _decode(data, comp, d_array_length, f_type, d_type):
    """
    Decode ms-numpress, b64 and/or zlib compressed data.

    Args:
        data (str): compressed data
        comp (str): compression method
        d_array_length (int): length of the uncompressed data array
        fType (str): float type (32 or 64 bit)
        d_type (str): type of data (mz, i, or time)

    Returns:
        result (tuple(str, list)): tuple containing the datatype and the
        decompressed data list.
    """
    if f_type == '32-bit float':
        if np is not None:
            f_type = np.float32
        else:
            f_type = 'f'
    elif f_type == '64-bit float':
        if np is not None:
            f_type = np.float64
        else:
            f_type = 'd'
    else:
        f_type = None
    decoded_data = b64dec(data)
    if 'zlib' in comp or \
            'zlib compression'in comp:
        decoded_data = zlib.decompress(decoded_data)

    if 'ms-np-linear' in comp \
            or 'ms-np-pic' in comp \
            or 'ms-np-slof' in comp \
            or 'MS-Numpress linear prediction compression' in comp \
            or 'MS-Numpress short logged float compression' in comp:
        result = []
        # start ms numpress decoder globally?
        if 'ms-np-linear' in comp \
                or 'MS-Numpress linear prediction compression' in comp:
            result = pymzml.MSDecoder.decodeLinear(decoded_data)
        elif 'ms-np-pic' in comp:
            result = pymzml.MSDecoder.decode_pic(decoded_data)
        elif 'ms-np-slof' in comp \
                or 'MS-Numpress short logged float compression' in comp:
            result = pymzml.MSDecoder.decode_slof(decoded_data)
        return (d_type, result)

    if np is not None:
        array = np.fromstring(decoded_data, f_type)
    else:
        fmt   = "{endian}{array_length}{float_type}".format(
            endian       = '<',
            array_length = d_array_length,
            float_type   = f_type
        )
        array = struct.unpack(fmt, decoded_data)
    return (d_type, array)


class Decoder:
    """
    Decoder class to enable parallel decoding of peaks.

    Keyword Args:
        nb_worker(int): number of pool workers to use. Defaults to 2.
    """
    def __init__(self, nb_workers=2):
        """
        """
        self._mz = None
        self._i  = None

    # @profile
    def pool_decode(self, data, callback):
        """
        Decode mz and i values in parallel.

        Args:
            data (): ...

        Keyword Args:
            callback (:obj:`func`): Callback function to call if decoding is
                finished. Should be :py:meth:`~pymzml.spec.Spectrum._register`.
        """
        ZE_POOL = Pool(processes=2)

        ZE_POOL.starmap(
            _decode,
            data
        )

    def _error_callback(self, result):
        """
        """
        raise Exception('Failed with error:\n{0}'.format(result))


if __name__ == '__main__':
    print(__doc__)
