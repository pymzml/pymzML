#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
The MsData class offers a base class for mass spectrometry data.
It provides common functionality for both Spectrum and Chromatogram classes.
"""

# Python mzML module - pymzml
# Copyright (C) 2010-2019 M. Kösters, C. Fufezan
#     The MIT License (MIT)

#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:

#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.

#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.

import math
import re
import sys
import warnings
import xml.etree.ElementTree as ElementTree
import zlib
from base64 import b64decode as b64dec
from collections import defaultdict as ddict
from struct import unpack

import numpy as np

from .obo import OboTranslator


class MsData(object):
    """
    General base class for mass spectrometry data handling.
    Provides common functionality for both Spectrum and Chromatogram classes.
    """

    def _read_accessions(self):
        """Set all required variables for this spectrum."""
        self.accessions = {}
        for element in self.element.iter():
            accession = element.get("accession")
            name = element.get("name")
            if accession is not None:
                self.accessions[name] = accession
        if "profile spectrum" in self.accessions.keys():
            self._profile = True

    def get_element_by_name(self, name):
        """
        Get element from the original tree by it's unit name.

        Arguments:
            name (str): unit name of the mzml element.

        Keyword Arguments:
            obo_version (str, optional): obo version number.

        """
        iterator = self.element.iter()
        return_ele = None
        for ele in iterator:
            if ele.get("name", default=None) == name:
                return_ele = ele
                break
        return return_ele

    def get_element_by_path(self, hooks):
        """
        Find elements in spectrum by its path.

        Arguments:
            hooks (list): list of parent elements for the target element.

        Returns:
            elements (list): list of XML objects
            found in the path

        Example:

            To access cvParam in scanWindow tag:

            >>> spec.get_element_by_path(['scanList', 'scan', 'scanWindowList',
            ...     'scanWindow', 'cvParam'])

        """
        return_ele = None
        if len(hooks) > 0:
            path_array = ["."]
            for hook in hooks:
                path_array.append("{ns}{hook}".format(ns=self.ns, hook=hook))
            path = "/".join(path_array)
            return_ele = self.element.findall(path)

        return return_ele

    def _register(self, decoded_tuple):
        d_type, array = decoded_tuple
        if d_type == "mz":
            self._mz = array
        elif d_type == "i":
            self._i = array
        elif d_type == "time":
            self._time = array
        else:
            raise Exception("Unknown data Type ({0})".format(d_type))

    def _get_encoding_parameters(self, array_type):
        """
        Find the correct parameter for decoding and return them as tuple.

        Arguments:
            array_type (str): data type of the array, e.g. m/z, time or
                intensity
        Returns:
            data (str)           : encoded data
            comp (str)           : compression method
            d_type (str)         : data type
            d_array_length (str) : length of the data array
        """
        numpress_encoding = False

        b_data_string = "./{ns}binaryDataArrayList/{ns}binaryDataArray/{ns}cvParam[@name='{name}']/..".format(
            ns=self.ns, name=array_type
        )
        float_type_string = "./{ns}cvParam[@accession='{Acc}']"

        b_data_array = self.element.find(b_data_string)
        if not b_data_array:
            # non-standard data array
            b_data_string = "./{ns}binaryDataArrayList/{ns}binaryDataArray/{ns}cvParam[@value='{value}']/..".format(
                ns=self.ns, value=array_type
            )
            b_data_array = self.element.find(b_data_string)

        comp = []
        if b_data_array:
            for cvParam in b_data_array.iterfind("./{ns}cvParam".format(ns=self.ns)):
                if "compression" in cvParam.get("name"):
                    if "numpress" in cvParam.get("name").lower():
                        numpress_encoding = True
                    comp.append(cvParam.get("name"))
                d_array_length = self.element.get("defaultArrayLength")
            if not numpress_encoding:
                try:
                    # 32-bit float
                    d_type = b_data_array.find(
                        float_type_string.format(
                            ns=self.ns,
                            Acc=self.obo_translator["32-bit float"]["id"],
                        )
                    ).get("name")
                except:
                    try:
                        # 64-bit Float
                        d_type = b_data_array.find(
                            float_type_string.format(
                                ns=self.ns,
                                Acc=self.obo_translator["64-bit float"]["id"],
                            )
                        ).get("name")
                    except:
                        try:
                            # 32-bit integer
                            d_type = b_data_array.find(
                                float_type_string.format(
                                    ns=self.ns,
                                    Acc=self.obo_translator["32-bit integer"]["id"],
                                )
                            ).get("name")
                        except:
                            try:
                                # 64-bit integer
                                d_type = b_data_array.find(
                                    float_type_string.format(
                                        ns=self.ns,
                                        Acc=self.obo_translator["64-bit integer"]["id"],
                                    )
                                ).get("name")
                            except:
                                # null-terminated ASCII string
                                d_type = b_data_array.find(
                                    float_type_string.format(
                                        ns=self.ns,
                                        Acc=self.obo_translator[
                                            "null-terminated ASCII string"
                                        ]["id"],
                                    )
                                ).get("name")
            else:
                # compression is numpress, dont need data type here
                d_type = None
            data = b_data_array.find("./{ns}binary".format(ns=self.ns))
            if data is not None:
                data = data.text
        else:
            data = None
            d_array_length = 0
            d_type = "64-bit float"
        if data is not None:
            data = data.encode("utf-8")
        else:
            data = ""
        return (data, d_array_length, d_type, comp)

    @property
    def measured_precision(self):
        """
        Set the measured and internal precision.

        Returns:
            value (float): measured Precision (e.g. 5e-6)
        """
        return self._measured_precision

    @measured_precision.setter
    def measured_precision(self, value):
        self._measured_precision = value
        self.internal_precision = int(round(50000.0 / (value * 1e6)))
        return

    def _decode_to_numpy(self, data, d_array_length, data_type, comp):
        """
        Decode the b64 encoded and packed strings from data as numpy arrays.

        Returns:
            data (np.ndarray): Returns the unpacked data as a tuple. Returns an
                               empty list if there is no raw data or raises an
                               exception if data could not be decoded.

        d_array_length just for compatibility
        """
        out_data = b64dec(data)
        if len(out_data) != 0:
            if "zlib" in comp or "zlib compression" in comp:
                out_data = zlib.decompress(out_data)
            if (
                "ms-np-linear" in comp
                or "ms-np-pic" in comp
                or "ms-np-slof" in comp
                or "MS-Numpress linear prediction compression" in comp
                or "MS-Numpress short logged float compression" in comp
            ):
                out_data = self._decodeNumpress_to_array(out_data, comp)
            if data_type == "32-bit float":
                # one character code may be sufficient too (f)
                f_type = np.float32
                out_data = np.frombuffer(out_data, f_type)
            elif data_type == "64-bit float":
                # one character code may be sufficient too (d)
                f_type = np.float64
                out_data = np.frombuffer(out_data, f_type)
            elif data_type == "32-bit integer":
                # one character code may be sufficient too (i)
                i_type = np.int32
                out_data = np.frombuffer(out_data, i_type)
            elif data_type == "64-bit integer":
                # one character code may be sufficient too (l)
                i_type = np.int64
                out_data = np.frombuffer(out_data, i_type)
            # TODO elif data_type == "null-terminated ASCII string":
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
        else:
            out_data = np.array([])
        return out_data

    def _decode_to_tuple(self, data, d_array_length, float_type, comp):
        """
        Decode b64 encoded and packed strings.

        Returns:
            data (tuple): Returns the unpacked data as a tuple.
                Returns an empty list if there is no raw data or
                raises an exception if data could not be decoded.
        """
        dec_data = b64dec(data)
        if len(dec_data) != 0:
            if "zlib" in comp or "zlib compression" in comp:
                dec_data = zlib.decompress(dec_data)
            if set(["ms-np-linear", "ms-np-pic", "ms-np-slof"]) & set(comp):
                self._decodeNumpress(data, comp)
            # else:
            #     print(
            #         'New data compression ({0}) detected, cant decompress'.format(
            #             comp
            #         )
            #     )
            #     sys.exit(1)
            if float_type == "32-bit float":
                f_type = "f"
            elif float_type == "64-bit float":
                f_type = "d"
            fmt = "{endian}{array_length}{float_type}".format(
                endian="<", array_length=d_array_length, float_type=f_type
            )
            ret_data = unpack(fmt, dec_data)
        else:
            ret_data = []
        return ret_data

    def _decodeNumpress_to_array(self, data, compression):
        """
        Decode golomb-rice encoded data (aka numpress encoded data).

        Arguments:
            data (str)        : Encoded data string
            compression (str) : Decompression algorithm to be used
                (valid are 'ms-np-linear', 'ms-np-pic', 'ms-np-slof')

        Returns:
            array (list): Returns the unpacked data as an array of floats.

        """
        result = []
        comp_ms_tags = [self.calling_instance.OT[comp]["id"] for comp in compression]
        data = np.frombuffer(data, dtype=np.uint8)
        if "MS:1002312" in comp_ms_tags:
            from .decoder import MSDecoder

            result = MSDecoder.decode_linear(data)
        elif "MS:1002313" in comp_ms_tags:
            from .decoder import MSDecoder

            result = MSDecoder.decode_pic(data)
        elif "MS:1002314" in comp_ms_tags:
            from .decoder import MSDecoder

            result = MSDecoder.decode_slof(data)
        return result

    def _median(self, data):
        """
        Compute median.

        Arguments:
            data (list): list of numeric values

        Returns:
            median (float): median of the input data
        """
        return np.median(data)

    def to_string(self, encoding="latin-1", method="xml"):
        """
        Return string representation of the xml element the
        spectrum was initialized with.

        Keyword Arguments:
            encoding (str) : text encoding of the returned string.\n
                             Default is latin-1.
            method (str)   : text format of the returned string.\n
                             Default is xml, alternatives are html and text.

        Returns:
            element (str)  : xml string representation of the spectrum.
        """
        return ElementTree.tostring(self.element, encoding=encoding, method=method)
