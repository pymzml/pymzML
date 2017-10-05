# distutils: language = c++
"""
Inspired by .... updated to work with
a) numpy or not ...

"""

from libc.stdlib cimport malloc, free
from libcpp.vector cimport vector as libcpp_vector
from cython.operator cimport dereference as deref, preincrement as inc, address as address
from MSNumpress cimport encodeLinear as _encodeLinear
from MSNumpress cimport decodeLinear as _decodeLinear
from MSNumpress cimport optimalLinearFixedPoint as _optimalLinearFixedPoint
from MSNumpress cimport encodeSlof as _encodeSlof
from MSNumpress cimport decodeSlof as _decodeSlof
from MSNumpress cimport optimalSlofFixedPoint as _optimalSlofFixedPoint
from MSNumpress cimport encodePic as _encodePic
from MSNumpress cimport decodePic as _decodePic

import cython

import numpy as np
cimport numpy as np


cdef class MSNumpress:
    cdef list decoded_data
    cdef list encoded_data

    def __init__(self, data):
        """
        """
        if isinstance(data, list):
            self.decoded_data = data
        elif isinstance(data, bytearray):
            self.encoded_data = data
        else:
            raise Exception('Data must be either list or bytearray')

    @property
    def encoded_data(self):
        """
        """
        return self.encoded_data

    @property
    def decoded_data(self):
        """
        """
        return self.decoded_data

    cpdef optimal_linear_fixed_point(self, data):
        """
        """
        dataSize = len(data)
        cdef libcpp_vector[double] c_data = data

        cdef double result = _optimalLinearFixedPoint( &c_data[0], dataSize)

        return result

    cpdef optimal_slof_fixed_point(self, data):
        """
        """
        dataSize = len(data)
        cdef libcpp_vector[double] c_data = data
        cdef double result = _optimalSlofFixedPoint( &c_data[0], dataSize)
        return result

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    def encode_linear(self, np.ndarray[double] data, double fp):
        cdef unsigned char * res_view = <unsigned char *>malloc(data.size * 5 + 8)
        cdef size_t res_len
        cdef size_t dataSize = data.size
        res_len = _encodeLinear(&data[0], dataSize, &res_view[0], fp)
        return np.frombuffer(res_view[:res_len], dtype=np.uint8) # 3.20

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    def decode_linear(self, np.ndarray[unsigned char] data):
        cdef list result = []
        cdef libcpp_vector[unsigned char] c_data = data
        cdef libcpp_vector[double] c_result

        _decodeLinear(c_data, c_result)

        cdef libcpp_vector[double].iterator it_result = c_result.begin()
        while it_result != c_result.end():
            result.append( deref(it_result) )
            inc(it_result)
        self.decoded_data = result
        return result

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    def encode_slof(self, np.ndarray[double] data, double fp):
        cdef unsigned char * res_view = <unsigned char *>malloc(data.size * 2 + 8)
        cdef size_t res_len
        cdef size_t dataSize = data.size
        res_len = _encodeSlof(&data[0], dataSize, &res_view[0], fp)
        return np.frombuffer(res_view[:res_len], dtype=np.uint8) # 3.20

    def decode_slof(self, data):
        cdef list result = []
        cdef libcpp_vector[unsigned char] c_data = data
        cdef libcpp_vector[double] c_result

        _decodeSlof(c_data, c_result)

        cdef libcpp_vector[double].iterator it_result = c_result.begin()
        while it_result != c_result.end():
            result.append( deref(it_result) )
            inc(it_result)
        self.decoded_data = result
        return result

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    def encode_pic(self, np.ndarray[double] data):
        cdef unsigned char * res_view = <unsigned char *>malloc(data.size * 5)
        cdef size_t res_len
        cdef size_t dataSize = data.size
        res_len = _encodePic(&data[0], dataSize, &res_view[0])
        return np.frombuffer(res_view[:res_len], dtype=np.uint8) # 3.20

    def decode_pic(self, data):
        cdef list result = []
        cdef libcpp_vector[unsigned char] c_data = data
        cdef libcpp_vector[double] c_result

        _decodePic(c_data, c_result)

        cdef libcpp_vector[double].iterator it_result = c_result.begin()
        while it_result != c_result.end():
            result.append( deref(it_result) )
            inc(it_result)
        self.decoded_data = result
        return result

