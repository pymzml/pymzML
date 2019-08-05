#!usr/bin/env python3
# -*- coding: latin-1 -*-
"""
The spectrum class offers a python object for mass spectrometry data.
The spectrum object holds the basic information of the spectrum and offers
methods to interrogate properties of the spectrum.
Data, i.e. mass over charge (m/z) and intensity decoding is performed on demand
and can be accessed via their properties, e.g. :py:attr:`~pymzml.spec.Spectrum.peaks`.

The Spectrum class is used in the :py:class:`~pymzml.run.Reader` class.
There each spectrum is accessible as a spectrum object.

Theoretical spectra can also be created using the setter functions.
For example, m/z values, intensities, and peaks can be set by the
corresponding properties: :py:attr:`pymzml.spec.Spectrum.mz`,
:py:attr:`pymzml.spec.Spectrum.i`, :py:attr:`pymzml.spec.Spectrum.peaks`.

Similar to the spectrum class, the chromatogram class allows interrogation
with profile data (time, intensity) in an total ion chromatogram.
"""
#
# pymzml
#
# Copyright (C) 2016 M. Kösters, C. Fufezan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import re
import sys
import warnings
import xml.etree.ElementTree as ElementTree
import zlib
from base64 import b64decode as b64dec
from collections import defaultdict as ddict
from functools import lru_cache
from operator import itemgetter as itemgetter
from struct import unpack

import numpy as np

from . import regex_patterns
from .decoder import MSDecoder

PROTON = 1.00727646677
ISOTOPE_AVERAGE_DIFFERENCE = 1.002


class MS_Spectrum(object):
    """
    General spectrum class for data handling.
    """

    # __slots__ = [
    #     # '_read_accessions',
    #     # 'get_element_by_name',
    #     # 'get_element_by_path',
    #     # '_register',
    #     # 'precursors',
    #     # '_get_encoding_parameters',
    #     # 'measured_precision',
    #     # '_decode_to_numpy',
    #     # '_median',
    #     # 'to_string',
    # ]
    def __init__(self):
        """."""
        pass

    def _read_accessions(self):
        """Set all required variables for this spectrum."""
        self.accessions = {}
        for element in self.element.getiterator():
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

    @property
    def precursors(self):
        """
        List the precursor information of this spectrum, if available.

        Returns:
            precursor(list): list of precursor ids for this spectrum.
        """
        if self._precursors is None:
            precursors = self.element.findall(
                "./{ns}precursorList/{ns}precursor".format(ns=self.ns)
            )
            self._precursors = []
            for prec in precursors:
                spec_ref = prec.get("spectrumRef")
                self._precursors.append(
                    regex_patterns.SPECTRUM_ID_PATTERN.search(spec_ref).group(1)
                )
        return self._precursors

    def _get_encoding_parameters(self, array_type):
        """
        Find the correct parameter for decoding and return them as tuple.

        Arguments:
            array_type (str): data type of the array, e.g. m/z, time or
                intensity
        Returns:
            data (str)           : encoded data
            comp (str)           : compression method
            fType (str)          : float precision
            d_array_length (str) : length of the data array
        """
        numpress_encoding = False

        # array_type_accession = self.calling_instance.OT[array_type]["id"]

        b_data_string = "./{ns}binaryDataArrayList/{ns}binaryDataArray/{ns}cvParam[@name='{Acc}']/..".format(
            ns=self.ns, Acc=array_type
        )

        float_type_string = "./{ns}cvParam[@accession='{Acc}']"

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
                    f_type = b_data_array.find(
                        float_type_string.format(
                            ns=self.ns,
                            Acc=self.calling_instance.OT["32-bit float"]["id"],
                        )
                    ).get("name")
                except:
                    # 64-bit Float
                    f_type = b_data_array.find(
                        float_type_string.format(
                            ns=self.ns,
                            Acc=self.calling_instance.OT["64-bit float"]["id"],
                        )
                    ).get("name")
            else:
                # compression is numpress, dont need floattype here
                f_type = None
            data = b_data_array.find("./{ns}binary".format(ns=self.ns)).text
        else:
            data = None
            d_array_length = 0
            f_type = "64-bit float"
        if data is not None:
            data = data.encode("utf-8")
        else:
            data = ""
        return (data, d_array_length, f_type, comp)

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

    def _decode_to_numpy(self, data, d_array_length, float_type, comp):
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
            if float_type == "32-bit float":
                # one character code may be sufficient too (f)
                f_type = np.float32
                out_data = np.frombuffer(out_data, f_type)
            elif float_type == "64-bit float":
                # one character code may be sufficient too (d)
                f_type = np.float64
                out_data = np.frombuffer(out_data, f_type)
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
            result = MSDecoder.decode_linear(data)
        elif "MS:1002313" in comp_ms_tags:
            result = MSDecoder.decode_pic(data)
        elif "MS:1002314" in comp_ms_tags:
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


class Spectrum(MS_Spectrum):
    """
    Spectrum class which inherits from class :py:attr:`pymzml.spec.MS_Spectrum`

    Arguments:
        element (xml.etree.ElementTree.Element): spectrum as xml element

    Keyword Arguments:
        measured_precision (float): in ppm, i.e. 5e-6 equals to 5 ppm.

    """

    def __init__(self, element=ElementTree.Element(""), measured_precision=5e-6):

        __slots__ = [
            "_centroided_peaks",
            "_centroided_peaks_sorted_by_i",
            "_deconvoluted_peaks",
            "_extreme_values",
            "_i",
            "_ID",
            "_id_dict",
            "_index",
            "_measured_precision",
            "_peaks",
            "_precursors",
            "_profile",
            "_reprofiled_peaks",
            "_t_mass_set",
            "_t_mz_set",
            "_time",
            "_transformed_mass_with_error",
            "_transformed_mz_with_error",
            "_transformed_peaks" "calling_instance" "element",
            "internal_precision" "noise_level_estimate",
            "selected_precursors",
        ]

        self._centroided_peaks = None
        self._centroided_peaks_sorted_by_i = None
        self._extreme_values = None
        self._i = None
        self._ID = None
        self._id_dict = None
        self._index = None
        self._ms_level = None
        self._mz = None
        self._peak_dict = {
            "raw": None,
            "centroided": None,
            "reprofiled": None,
            "deconvoluted": None,
        }
        self._selected_precursors = None
        self._profile = None
        self.reprofiled = False
        self._reprofiled_peaks = None
        self._scan_time = None
        self._scan_time_unit = None
        self._t_mass_set = None
        self._t_mz_set = None
        self._TIC = None
        self._transformed_mass_with_error = None
        self._transformed_mz_with_error = None
        self._transformed_peaks = None
        self.calling_instance = None
        self.element = element
        self.measured_precision = measured_precision
        self.noise_level_estimate = {}

        self.ns = ""
        if self.element:
            self.ns = (
                re.match(r"\{.*\}", element.tag).group(0)
                if re.match(r"\{.*\}", element.tag)
                else ""
            )

        self._decode = self._decode_to_numpy
        self._array = np.array

    def __del__(self):
        """
        Clear self.element to limit RAM usage
        """
        if self.element:
            self.element.clear()

    def __add__(self, other_spec):
        """
        Adds two pymzml spectra

        Arguments:
            other_spec (Spectrum): spectrum to add to the current spectrum

        Returns:
            self (Spectrum): reference to the edited spectrum

        Example:

        >>> import pymzml
        >>> s = pymzml.spec.Spectrum( measuredPrescision = 20e-6 )
        >>> file_to_read = "../mzML_example_files/xy.mzML.gz"
        >>> run = pymzml.run.Reader(
        ...     file_to_read ,
        ...     MS1_Precision = 5e-6 ,
        ...     MSn_Precision = 20e-6
        ... )
        >>> for spec in run:
        ...     s += spec

        """
        assert isinstance(other_spec, Spectrum)
        if self._peak_dict["reprofiled"] is None:
            reprofiled = self._reprofile_Peaks()
            self.set_peaks(reprofiled, "reprofiled")
        for mz, i in other_spec.peaks("reprofiled"):
            self._peak_dict["reprofiled"][mz] += i
        return self

    def __sub__(self, other_spec):
        """
        Subtracts two pymzml spectra.

        Arguments:
            other_spec (spec.Spectrum): spectrum to subtract from the current
                spectrum

        Returns:
            self (spec.Spectrum): returns self after other_spec was subtracted
        """
        assert isinstance(other_spec, Spectrum)
        if self._peak_dict["reprofiled"] is None:
            self.set_peaks(self._reprofile_Peaks(), "reprofiled")
        for mz, i in other_spec.peaks("reprofiled"):
            self._peak_dict["reprofiled"][mz] -= i
        self.set_peaks(None, "centroided")
        self.set_peaks(None, "raw")
        return self

    def __mul__(self, value):
        """
        Multiplies each intensity with a float, i.e. scales the spectrum.

        Arguments:
            value (int, float): value to multiply the intensities with

        Returns:
            self (spec.Spectrum): returns self after intensities were scaled
                by value
        """
        assert isinstance(value, (int, float))
        if self._peak_dict["raw"] is not None:
            self.set_peaks(
                np.column_stack(
                    (self.peaks("raw")[:, 0], self.peaks("raw")[:, 1] * value)
                ),
                "raw",
            )
        if self._peak_dict["centroided"] is not None:
            self.set_peaks(
                np.column_stack(
                    (self.centroided_peaks[:, 0], self.centroided_peaks[:, 1] * value)
                ),
                "centroided",
            )
        if self._peak_dict["reprofiled"] is not None:
            for mz in self._peak_dict["reprofiled"].keys():
                self._peak_dict["reprofiled"][mz] *= float(value)
        return self

    def __truediv__(self, value):
        """
        Divides each intensity by a float, i.e. scales the spectrum.

        Arguments:
            value (int, float): value to divide the intensities by

        Returns:
            self (spec.Spectrum): returns self after intensities were scaled
                by value.
        """
        for mz, i in self.peaks("reprofiled"):
            self._peak_dict["reprofiled"][mz] /= float(value)
        if self._peak_dict["raw"] is not None:
            if len(self._peak_dict['raw']) != 0:
                self.set_peaks(
                    np.column_stack(
                        (self.peaks("raw")[:, 0], self.peaks("raw")[:, 1] / float(value))
                    ),
                    "raw",
                )
        if self._peak_dict["centroided"] is not None:
            peaks = self._peak_dict['centroided']
            scaled_peaks = peaks[:,1] / value
            peaks[:,1] = scaled_peaks
            # self.set_peaks(peaks, "centroided")
            self._peak_dict['centroided'] = peaks
        return self

    def __div__(self, value):
        """
        Integer division is the same as __truediv__ for this class
        """
        return self.__truediv__(value)

    def __repr__(self):
        """
        Returns representative string for a spectrum object class
        """
        return "<__main__.Spectrum object with native ID {0} at {1}>".format(
            self.ID, hex(id(self))
        )

    def __str__(self):
        """
        Returns representative string for a spectrum object class
        """
        return "<__main__.Spectrum object with native ID {0} at {1}>".format(
            self.ID, hex(id(self))
        )

    @lru_cache()
    def __getitem__(self, accession):
        """
        Access spectrum XML information by tag name

        Args:
            accession(str): name of the XML tag

        Returns:
            value (float or str): value of the XML tag
        """
        #  TODO implement cache???
        if accession == "id":
            return_val = self.ID
        else:
            if not accession.startswith("MS:"):
                accession = self.calling_instance.OT[accession]["id"]
            search_string = './/*[@accession="{0}"]'.format(accession)

            elements = []
            for x in self.element.iterfind(search_string):
                val = x.attrib.get("value")
                try:
                    val = float(val)
                except:
                    pass
                elements.append(val)

            if len(elements) == 0:
                return_val = None
            elif len(elements) == 1:
                return_val = elements[0]
            else:
                return_val = elements
        return return_val

    def get(self, acc, default=None):
        """Mimic dicts get function.

        Args:
            acc (str): accession or obo tag to return
            default (None, optional): default value if acc is not found
        """
        val = self[acc]
        if val is None:
            val = default
        return val

    def __contains__(self, value):
        """Check if MS tag or name can be found in spectrum.

        Args:
            value (str): MS tag or OBO name

        Returns:
            bool
        """
        r = False
        if self[value] is not None:
            r = True
        return r

    @property
    def measured_precision(self):
        """
        Sets the measured and internal precision

        Returns:
            value (float): measured precision (e.g. 5e-6)
        """
        return self._measured_precision

    @measured_precision.setter
    def measured_precision(self, value):
        self._measured_precision = value
        self.internal_precision = int(round(50000.0 / (value * 1e6)))
        return

    @property
    def t_mz_set(self):
        """
        Creates a set of integers out of transformed m/z values
        (including all values in the defined imprecision).
        This is used to accelerate has_peak function and similar.

        Returns:
            t_mz_set (set): set of transformed m/z values
        """
        if self._t_mz_set is None:
            self._t_mz_set = set()
            for mz, i in self.peaks("centroided"):
                self._t_mz_set |= set(
                    range(
                        int(
                            round(
                                (mz - (mz * self.measured_precision))
                                * self.internal_precision
                            )
                        ),
                        int(
                            round(
                                (mz + (mz * self.measured_precision))
                                * self.internal_precision
                            )
                        )
                        + 1,
                    )
                )
        return self._t_mz_set

    @property
    def transformed_mz_with_error(self):
        """
        Returns transformed m/z value with error

        Returns:
            tmz values (dict): Transformed m/z values in dictionary\n
                {\n
                m/z_with_error : [(m/z,intensity), ...], ...\n
                }\n
        """
        if self._transformed_mz_with_error is None:
            self._transformed_mz_with_error = ddict(list)
            for mz, i in self.peaks("centroided"):
                for t_mz_with_error in range(
                    int(
                        round(
                            (mz - (mz * self.measured_precision))
                            * self.internal_precision
                        )
                    ),
                    int(
                        round(
                            (mz + (mz * self.measured_precision))
                            * self.internal_precision
                        )
                    )
                    + 1,
                ):
                    self._transformed_mz_with_error[t_mz_with_error].append((mz, i))
        return self._transformed_mz_with_error

    @property
    def transformed_peaks(self):
        """
        m/z value is multiplied by the internal precision.

        Returns:
            Transformed peaks (list): Returns a list of peaks (tuples of mz and
            intensity).
            Float m/z values are adjusted by the internal precision
            to integers.
        """
        if self._transformed_peaks is None:
            self._transformed_peaks = [
                (self.transform_mz(mz), i) for mz, i in self.peaks("centroided")
            ]
        return self._transformed_peaks

    @property
    def TIC(self):
        """
        Property to access the total ion current for this spectrum.

        Returns:
            TIC (float): Total Ion Current of the spectrum.
        """
        if self._TIC is None:
            self._TIC = float(
                self.element.find(
                    "./{ns}cvParam[@accession='MS:1000285']".format(ns=self.ns)
                ).get("value")
            )  # put hardcoded MS tags in minimum.py???
        return self._TIC

    @property
    def ID(self):
        """
        Access the native id (last number in the id attribute) of the spectrum.

        Returns:
            ID (str): native ID of the spectrum
        """
        if self._ID is None:
            if self.element:
                match = regex_patterns.SPECTRUM_ID_PATTERN.search(
                    self.element.get("id", None)
                )
                if match:
                    try:
                        self._ID = int(match.group(1))
                    except ValueError:
                        self._ID = match.group(1)
                else:
                    self._ID = ""
        return self._ID

    @property
    def id_dict(self):
        """
        Access to all entries stored the id attribute of a spectrum.

        Returns:
            id_dict (dict): key value pairs for all entries in id attribute of a spectrum
        """
        if self._id_dict is None:
            tuples = []
            captures = regex_patterns.SPECTRUM_PATTERN3.match(
                self.element.attrib["id"]
            ).captures(1)
            for element in captures:
                k, v = element.strip().split("=")
                v = int(v)
                tuples.append([k, v])
            self._id_dict = dict(tuples)
        return self._id_dict

    @property
    def index(self):
        """
        Access the index of the spectrum.

        Returns:
            index (int): index of the spectrum

        Note:
            This does not necessarily correspond to the native spectrum ID
        """
        if self._index is None:
            self._index = self.element.get("index")
            try:
                self._index = int(self._index)
            except:
                pass
        return self._index

    @property
    def ms_level(self):
        """
        Property to access the ms level.

        Returns:
            ms_level (int):
        """
        if self._ms_level is None:
            self._ms_level = self.element.find(
                ".//{ns}cvParam[@accession='MS:1000511']".format(ns=self.ns)
            ).get(
                "value"
            )  # put hardcoded MS tags in minimum.py???
        return int(self._ms_level)

    @property
    def scan_time(self):
        """
        Property to access the retention time and retention time unit.
        Please note, that we do not assume the retention time unit,
        if it is not correctly defined in the mzML.
        It is set to 'unicorns' in this case.

        Returns:
            scan_time (float):
            scan_time_unit (str):
        """
        if self._scan_time is None or self._scan_time_unit is None:
            scan_time_ele = self.element.find(
                ".//*[@accession='MS:1000016']".format(ns=self.ns)
            )
            self._scan_time = float(scan_time_ele.attrib.get("value"))
            self._scan_time_unit = scan_time_ele.get("unitName", "unicorns")
        return self._scan_time, self._scan_time_unit

    # @property
    def scan_time_in_minutes(self):
        """
        Property to access the retention time in minutes.
        If the retention time unit is defined within the mzML,
        the retention time is converted into minutes and returned
        without the unit.

        Returns:
            scan_time (float):
        """

        self._scan_time, time_unit = self.scan_time
        if self._scan_time_unit.lower() == "second":
            self._scan_time /= 60.0
        elif self._scan_time_unit.lower() == "minute":
            pass
        elif self._scan_time_unit.lower() == "hour":
            self._scan_time *= 60.0
            pass
        else:
            raise Exception("Time unit '{0}' unknown".format(self._scan_time_unit))
        return self._scan_time

    @property
    def selected_precursors(self):
        """
        Property to access the selected precursors of a MS2 spectrum. Returns
        a list of dicts containing the precursors mz and, if available intensity
        and charge for each precursor.

        Returns:
            selected_precursors (list):
        """
        if self._selected_precursors is None:
            selected_precursor_mzs = self.element.findall(
                ".//*[@accession='MS:1000744']"
            )
            selected_precursor_is = self.element.findall(
                ".//*[@accession='MS:1000042']"
            )
            selected_precursor_cs = self.element.findall(
                ".//*[@accession='MS:1000041']"
            )

            mz_values = []
            i_values = []
            charges = []
            for obj in selected_precursor_mzs:
                mz = obj.get("value")
                mz_values.append(float(mz))
            for obj in selected_precursor_is:
                i = obj.get("value")
                i_values.append(float(i))
            for obj in selected_precursor_cs:
                c = obj.get("value")
                charges.append(int(c))
            self._selected_precursors = []
            for pos, mz in enumerate(mz_values):
                dict_2_save = {"mz": mz}
                for key, list_of_values in [("i", i_values), ("charge", charges)]:
                    try:
                        dict_2_save[key] = list_of_values[pos]
                    except:
                        continue
                self._selected_precursors.append(dict_2_save)

        return self._selected_precursors

    @property
    def mz(self):
        """
        Returns the list of m/z values. If the m/z values are encoded, the
        function :func:`~spec.MS_Spectrum._decode` is used to decode the encoded data.
        The mz property can also be set, e.g. for theoretical data.
        However, it is recommended to use the peaks property to set mz and
        intensity tuples at same time.

        Returns:
            mz (list): list of m/z values of spectrum.
        """
        if self._mz is None:
            params = self._get_encoding_parameters("m/z array")
            self._mz = self._decode(*params)
        return self._mz

    @mz.setter
    def mz(self, mz_list):
        """"""
        mz_list = np.array(mz_list, dtype=np.float64)
        mz_list.sort()
        self._mz = mz_list

    @property
    def i(self):
        """
        Returns the list of the intensity values.
        If the intensity values are encoded, the function :func:`~spec.MS_Spectrum._decode`
        is used to decode the encoded data.\n
        The i property can also be set, e.g. for theoretical data. However,
        it is recommended to use the peaks property to set mz and intensity
        tuples at same time.

        Returns
            i (list): list of intensity values from the analyzed spectrum
        """
        if self._i is None:
            params = self._get_encoding_parameters("intensity array")
            self._i = self._decode(*params)
        return self._i

    @i.setter
    def i(self, intensity_list):
        self._i = np.array(intensity_list)

    def peaks(self, peak_type):
        """
        Decode and return a list of mz/i tuples.

        Args:
            peak_type(str): currently supported types are:
                raw, centroided and reprofiled

        Returns:
            peaks (list or ndarray): list or numpy array of mz/i tuples or arrays
        """
        if self._peak_dict[peak_type] is None:
            if self._peak_dict["raw"] is None:
                self._peak_dict["raw"] = []
                mz_params = self._get_encoding_parameters("m/z array")
                i_params = self._get_encoding_parameters("intensity array")
                mz = self._decode(*mz_params)
                i = self._decode(*i_params)
                # self._peak_dict['raw'] = np.ndarray(len(mz), dtype=tuple)
                for pos, mz_val in enumerate(mz):
                    self._peak_dict["raw"].append((mz_val, i[pos]))
                    # self._peak_dict['raw'][pos] = [mz, 1]
            if peak_type is "raw":
                pass
            elif peak_type is "centroided":
                self._peak_dict["centroided"] = self._centroid_peaks()
            elif peak_type is "reprofiled":
                self._peak_dict["reprofiled"] = self._reprofile_Peaks()
            elif peak_type is "deconvoluted":
                self._peak_dict["deconvoluted"] = self._deconvolute_peaks()
            else:
                raise KeyError

        peaks = self._array(self._peak_dict[peak_type])
        if peak_type is "reprofiled":
            peaks = list(self._peak_dict[peak_type].items())
            peaks.sort(key=itemgetter(0))
        return peaks

    def set_peaks(self, peaks, peak_type):
        """
        Assign a custom peak array of type peak_type

        Args:
            peaks(list or ndarray): list or array of mz/i values
            peak_type(str): Either raw, centroided or reprofiled

        """
        peak_type = peak_type.lower()
        if peak_type == "raw":
            # if not isinstance(peaks, np.ndarray):
            #     peaks = np.array(peaks)
            self._peak_dict["raw"] = peaks
            self._mz = [mz for mz, i in self.peaks("raw")]
            self._i = [i for mz, i in self.peaks("raw")]
        elif peak_type == "centroided":
            # if not isinstance(peaks, np.ndarray):
            #     peaks = np.array(peaks)
            self._peak_dict["centroided"] = peaks
            self._mz = [mz for mz, i in self.peaks("raw")]
            self._i = [i for mz, i in self.peaks("raw")]
        elif peak_type == "reprofiled":
            try:
                self._peak_dict["reprofiled"] = peaks
            except TypeError:
                self._peak_dict["reprofiled"] = None
        else:
            raise Exception(
                "Peak type is not suppported\n"
                'Choose either "raw", "centroided" or "reprofiled"'
            )

    def _centroid_peaks(self):
        """
        Perform a Gauss fit to centroid the peaks for the property
        centroided_peaks.

        Returns:
            centroided_peaks (list): list of centroided m/z, i tuples
        """
        try:
            acc = self.calling_instance.OT["profile spectrum"]["id"]
            is_profile = self.element.find(
                ".//*[@accession='{acc}']".format(ns=self.ns, acc=acc)
            )
        except (TypeError, AttributeError) as e:
            is_profile = False

        if is_profile or self.reprofiled:  # check if spec is a profile spec
            tmp = []
            if self._peak_dict["reprofiled"] is not None:
                i_array = [i for mz, i in self.peaks("reprofiled")]
                mz_array = [mz for mz, i in self.peaks("reprofiled")]
            else:
                i_array = self.i
                mz_array = self.mz
            for pos, i in enumerate(i_array[:-1]):
                if pos <= 1:
                    continue
                if 0 < i_array[pos - 1] < i > i_array[pos + 1] > 0:
                    x1 = float(mz_array[pos - 1])
                    y1 = float(i_array[pos - 1])
                    x2 = float(mz_array[pos])
                    y2 = float(i_array[pos])
                    x3 = float(mz_array[pos + 1])
                    y3 = float(i_array[pos + 1])
                    if x2 - x1 > (x3 - x2) * 10 or (x2 - x1) * 10 < x3 - x2:
                        continue
                    if y3 == y1:
                        y3 += 0.01 * y1

                    try:
                        double_log = math.log(y2 / y1) / math.log(y3 / y1)
                        mue = (double_log * (x1 * x1 - x3 * x3) - x1 * x1 + x2 * x2) / (
                            2 * (x2 - x1) - 2 * double_log * (x3 - x1)
                        )
                        c_squarred = (
                            x2 * x2 - x1 * x1 - 2 * x2 * mue + 2 * x1 * mue
                        ) / (2 * math.log(y1 / y2))
                        A = y1 * math.exp((x1 - mue) * (x1 - mue) / (2 * c_squarred))
                    except ZeroDivisionError:
                        continue
                    tmp.append((mue, A))
            return tmp
        else:
            return self.peaks("raw")

    def _reprofile_Peaks(self):
        """
        Performs reprofiling for property reprofiled_peaks.

        Returns:
            reprofiled_peaks (list): list of reprofiled m/z, i tuples
        """
        tmp = ddict(int)
        for mz, i in self.peaks("centroided"):
            # Let the measured precision be 2 sigma of the signal width
            # When using normal distribution
            # FWHM = 2 sqt(2 * ln(2)) sigma = 2.3548 sigma
            s = mz * self.measured_precision * 2  # in before 2
            s2 = s * s
            floor = mz - 5.0 * s  # Gauss curve +- 3 sigma
            ceil = mz + 5.0 * s
            ip = self.internal_precision / 4
            # more spacing, i.e. less points describing the gauss curve
            # -> faster adding
            for _ in range(int(round(floor * ip)), int(round(ceil * ip)) + 1):
                if _ % int(5) == 0:
                    a = float(_) / float(ip)
                    y = i * math.exp(-1 * ((mz - a) * (mz - a)) / (2 * s2))
                    tmp[a] += y
        self.reprofiled = True
        self.set_peaks(None, "centroided")
        return tmp

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

    def _mz_2_mass(self, mz, charge):
        """
        Calculate the uncharged mass for a given mz value

        Arguments:
            mz (float)  : m/z value
            charge(int) : charge

        Returns:
            mass (float): Returns mass of a given m/z value
        """
        return (mz - PROTON) * charge

    def _set_params_from_reference_group(self, ref_element):
        ref = self.element.find("{ns}referenceableParamGroupRef".format(ns=self.ns))
        if ref is not None:
            ref = ref.get("ref")
        ele = ref_element.find(".//*[@id='{ref}']".format(ref=ref, ns=self.ns))
        if ele is not None and ref == ele.get("id"):
            for param in ele.getiterator():
                self.element.append(ele)
                acc = param.get("accession")

    # Public functions

    def reduce(self, mz_range=(None, None)):
        """
        Remove all m/z values outside the given range.

        Arguments:
            mz_range (tuple): tuple of min, max values

        Returns:
            peaks (list): list of mz, i tuples in the given range.
        """
        assert isinstance(
            mz_range, tuple
        ), "Require tuple of (min,max) mz range to reduce spectrum"
        if mz_range != (None, None):
            tmp_peaks = []
            for mz, i in self.peaks("raw"):
                if mz < mz_range[0]:
                    continue
                elif mz > mz_range[1]:
                    break
                else:
                    tmp_peaks.append((mz, i))
            self.set_peaks(tmp_peaks, "raw")
        return self.peaks("raw")

    def remove_noise(self, mode="median", noise_level=None):
        """
        Function to remove noise from peaks, centroided peaks and reprofiled
        peaks.

        Keyword arguments:
                mode (str): define mode for removing noise. Default = "median"
                (other modes: "mean", "mad")
            noise_level (float): noise threshold

        Returns:
            reprofiled peaks (list): Returns a list with tuples of
            m/z-intensity pairs above the noise threshold

        """
        # Thanks to JD Hogan for pointing it out!
        callPeaks = self.peaks("raw")
        callcentPeaks = self.peaks("centroided")
        if noise_level is None:
            noise_level = self.estimated_noise_level(mode=mode)
        if self._peak_dict["centroided"] is not None:
            self._peak_dict["centroided"] = [
                (mz, i) for mz, i in self.peaks("centroided") if i >= noise_level
            ]
        if self._peak_dict["raw"] is not None:
            self._peak_dict["raw"] = [
                (mz, i) for mz, i in self.peaks("raw") if i >= noise_level
            ]
        self._peak_dict["reprofiled"] = None
        return self

    def estimated_noise_level(self, mode="median"):
        """
        Calculates noise threshold for function remove_noise.

        Different modes are available. Default is 'median'

        Keyword Arguments:
            mode (str): define mode for removing noise. Default = "median"
                (other modes: "mean", "mad")

        Returns:
            noise_level (float): estimate noise threshold


        """
        if len(self.peaks("centroided")) == 0:  # or is None?
            return_value = 0

        self.noise_level_estimate = {}
        if mode not in self.noise_level_estimate.keys():
            if mode == "median":
                self.noise_level_estimate["median"] = self._median(
                    [i for mz, i in self.peaks("centroided")]
                )
            elif mode == "mad":
                median = self.estimated_noise_level(mode="median")
                self.noise_level_estimate["mad"] = self._median(
                    sorted([abs(i - median) for mz, i in self.peaks("centroided")])
                )
            elif mode == "mean":
                self.noise_level_estimate["mean"] = sum(
                    [i for mz, i in self.peaks("centroided")]
                ) / float(len(self.peaks("centroided")))
            else:
                print(
                    "Do not understand noise level estimation method call with given mode: {0}".format(
                        mode
                    )
                )
            return_value = self.noise_level_estimate[mode]
        return return_value

    def highest_peaks(self, n):
        """
        Function to retrieve the n-highest centroided peaks of the spectrum.

        Arguments:
            n (int): number of highest peaks to return.

        Returns:
            centroided peaks (list): list mz, i tupls with n-highest

        Example:

        >>> run = pymzml.run.Reader(
        ...     "tests/data/example.mzML.gz",
        ...      MS_precisions =  {
        ...         1 : 5e-6,
        ...         2 : 20e-6
        ...     }
        ... )
        >>> for spectrum in run:
        ...     if spectrum.ms_level == 2:
        ...         if spectrum.ID == 1770:
        ...             for mz,i in spectrum.highest_peaks(5):
        ...                print(mz, i)

        """
        if self._centroided_peaks_sorted_by_i is None:
            self._centroided_peaks_sorted_by_i = sorted(
                self.peaks("centroided"), key=itemgetter(1)
            )
        return self._centroided_peaks_sorted_by_i[-n:]

    def ppm2abs(self, value, ppm_value, direction=1, factor=1):
        """
        Returns the value plus (or minus, dependent on direction) the
        error (measured precision ) for this value.

        Arguments:
            value (float)   : m/z value
            ppm_value (int)  : ppm value

        Keyword Arguments:
            direction (int) : plus or minus the considered m/z value.
                The argument *direction* should be 1 or -1
            factor (int)    : multiplication factor for the imprecision.
                The argument *factor* should be bigger than 0

        Returns:
            imprecision (float): imprecision for the given value

        """
        result = value + (value * (ppm_value * factor)) * direction
        return result

    def extreme_values(self, key):
        """
        Find extreme values, minimal and maximum m/z and intensity

        Arguments:
            key (str)       : m/z : "mz" or  intensity : "i"

        Returns:
            extrema (tuple) : tuple of minimal and maximum m/z or intensity

        """
        available_extreme_values = ["mz", "i"]
        if key not in available_extreme_values:
            print(
                "Do not understand extreme request: '{0}'; available values are: {1}".format(
                    key, available_extreme_values
                )
            )
            exit()
        if self._extreme_values is None:
            self._extreme_values = {}
        try:
            if key == "mz":
                all_mz_values = [mz for mz, i in self.peaks("raw")]
                self._extreme_values["mz"] = (min(all_mz_values), max(all_mz_values))
            else:
                all_i_values = [i for mz, i in self.peaks("raw")]
                self._extreme_values["i"] = (min(all_i_values), max(all_i_values))
        except ValueError:
            # emtpy spectrum
            self._extreme_values[key] = ()
        return self._extreme_values[key]

    def has_peak(self, mz2find):
        """
        Checks if a Spectrum has a certain peak.
        Requires a m/z value as input and returns a list of peaks if the m/z
        value is found in the spectrum, otherwise ``[]`` is returned.
        Every peak is a tuple of m/z and intensity.

        Note:
            Multiple peaks may be found, depending on the defined precisions

        Arguments:
            mz2find (float): m/z value which should be found

        Returns:
            peaks (list): list of m/z, i tuples

        Example:

        >>> import pymzml
        >>> example_file = 'tests/data/example.mzML'
        >>> run = pymzml.run.Reader(
        ...     example_file,
        ...     MS_precisions =  {
        ...         1 : 5e-6,
        ...         2 : 20e-6
        ...     }
        ... )
        >>> for spectrum in run:
        ...     if spectrum.ms_level == 2:
        ...             peak_to_find = spectrum.has_peak(1016.5404)
        ...             print(peak_to_find)
        [(1016.5404, 19141.735187697403)]

        """
        value = self.transform_mz(mz2find)
        return self.transformed_mz_with_error[value]

    def has_overlapping_peak(self, mz):
        """
        Checks if a spectrum has more than one peak for a given m/z value
        and within the measured precision

        Arguments:
            mz (float): m/z value which should be checked

        Returns:
            Boolean (bool): Returns ``True`` if a nearby peak is detected,
            otherwise ``False``
        """
        for minus_or_plus in [-1, 1]:
            target = self.ppm2abs(mz, self.measured_precision, minus_or_plus, 1)
            temp = self.has_peak(self.ppm2abs(mz, self.measured_precision))
            if temp and len(temp) > 1:
                return True
        return False

    def similarity_to(self, spec2, round_precision=0):
        """
        Compares two spectra and returns cosine

        Arguments:
            spec2 (Spectrum): another pymzml spectrum that is compared to the
                current spectrum.

        Keyword Arguments:
            round_precision (int): precision mzs are rounded to, i.e. round( mz,
                round_precision )

        Returns:
            cosine (float): value between 0 and 1, i.e. the cosine between the
                two spectra.

        Note:
            Spectra data is transformed into an n-dimensional vector,
            where m/z values are binned in bins of 10 m/z and the intensities
            are added up. Then the cosine is calculated between those two
            vectors. The more similar the specs are, the closer the value is
            to 1.
        """
        assert isinstance(spec2, Spectrum), "Spectrum 2 is not a pymzML spectrum"

        vector1 = ddict(int)
        vector2 = ddict(int)
        mzs = set()
        for mz, i in self.peaks("raw"):
            vector1[round(mz, round_precision)] += i
            mzs.add(round(mz, round_precision))
        for mz, i in spec2.peaks("raw"):
            vector2[round(mz, round_precision)] += i
            mzs.add(round(mz, round_precision))

        z = 0
        n_v1 = 0
        n_v2 = 0

        for mz in mzs:
            int1 = vector1[mz]
            int2 = vector2[mz]
            z += int1 * int2
            n_v1 += int1 * int1
            n_v2 += int2 * int2
        try:
            cosine = z / (math.sqrt(n_v1) * math.sqrt(n_v2))
        except:
            cosine = 0.0
        return cosine

    def transform_mz(self, value):
        """
        pymzml uses an internal precision for different tasks. This precision
        depends on the measured precision and is calculated when
        :py:attr:`spec.Spectrum.measured_precision` is invoked. transform_mz
        can be used to transform m/z values into the internal standard.

        Arguments:
            value (float): m/z value

        Returns:
            transformed value (float): to internal standard transformed mz
            value this value can be used to probe internal dictionaries,
            lists or sets, e.g. :func:`pymzml.spec.Spectrum.t_mz_set`

        Example:

            >>> import pymzml
            >>> run = pymzml.run.Reader(
            ...     "test.mzML.gz" ,
            ...     MS_precisions =  {
            ...         1 : 5e-6,
            ...         2 : 20e-6
            ...     }
            ... )
            >>>
            >>> for spectrum in run:
            ...     if spectrum.ms_level == 2:
            ...         peak_to_find = spectrum.has_deconvoluted_peak(
            ...             1044.5804
            ...         )
            ...         print(peak_to_find)
            [(1044.5596, 3809.4356300564586)]

        """
        return int(round(value * self.internal_precision))

    def deprecation_warning(self, function_name):
        deprecation_lookup = {
            "similarityTo": "similarity_to",
            "hasPeak": "has_peak",
            "extremeValues": "extreme_values",
            "transformMZ": "transform_mz",
            "hasOverlappingPeak": "has_overlapping_peak",
            "highestPeaks": "highest_peaks",
            "estimatedNoiseLevel": "estimated_noise_level",
            "removeNoise": "remove_noise",
            "newPlot": "new_plot",
            "centroidedPeaks": "peaks",
        }
        warnings.warn(
            """
            Function: "{0}" deprecated since version 1.0.0, please use new function: "{1}"
            """.format(
                function_name, deprecation_lookup.get(function_name, "not_defined_yet")
            ),
            DeprecationWarning,
        )

    def similarityTo(self, spec2, round_precision=0):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.similarity_to(spec2, round_precision=round_precision)

    def hasPeak(self, mz):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.has_peak(mz)

    def extremeValues(self, key):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.extreme_values(key)

    def transformMZ(self, value):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.transform_mz(value)

    def hasOverlappingPeak(self, mz):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.has_overlapping_peak(mz)

    def highestPeaks(self, n):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.highest_peaks(n)

    def estimatedNoiseLevel(self, mode="median"):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.estimated_noise_level(mode=mode)

    def removeNoise(self, mode="median", noiseLevel=None):
        self.deprecation_warning(sys._getframe().f_code.co_name)
        return self.remove_noise(mode=mode, noise_level=noiseLevel)

    @property
    def centroidedPeaks(self):
        # self.deprecation_warning( sys._getframe().f_code.co_name )
        return self.peaks("centroided")


class Chromatogram(MS_Spectrum):
    """
    Class for Chromatogram access and handling.
    """

    def __init__(self, element, measured_precision=5e-6, param=None):
        """
        Arguments:
            element (xml.etree.ElementTree.Element): spectrum as xml Element

        Keyword Arguments:
            measured_precision (float): in ppm, i.e. 5e-6 equals to 5 ppm.
            param (dict): parameter mapping for this spectrum
        """

        __slots__ = [
            "_measured_precision",
            "element",
            "noise_level_estimate",
            "_time",
            "_i",
            "_t_mass_set",
            "_peaks",
            "_t_mz_set",
            "_centroided_peaks",
            "_reprofiled_peaks",
            "_deconvoluted_peaks",
            "_profile",
            "_extreme_values",
            "_centroided_peaks_sorted_by_i",
            "_transformed_mz_with_error",
            "_transformed_mass_with_error",
            "_precursors",
            "_ID",
            "internal_precision",
        ]

        self._measured_precision = measured_precision
        self.element = element
        self.noise_level_estimate = {}
        # Property variables
        self._time = None
        self._ms_level = None
        self._i = None
        self._t_mass_set = None
        self._peaks = None
        self._t_mz_set = None
        self._centroided_peaks = None
        self._reprofiled_peaks = None
        self._deconvoluted_peaks = None
        self._profile = None
        self._extreme_values = None
        self._centroided_peaks_sorted_by_i = None
        self._transformed_mz_with_error = None
        self._transformed_mass_with_error = None
        self._precursors = None
        self._ID = None

        if self.element:
            # self._read_accessions()
            self.ns = (
                re.match(r"\{.*\}", element.tag).group(0)
                if re.match(r"\{.*\}", element.tag)
                else ""
            )
            # self._ns_paths            = {
            #     'mz'      : "{ns}binaryDataArrayList/" \
            #                 "{ns}binaryDataArray/" \
            #                 "{ns}cvParam[@accession='{Acc}']/..".format(
            #                     ns=self.ns,
            #                     Acc=self.accessions['time array']
            #             ),
            #     'i'       : "{ns}binaryDataArrayList/" \
            #                 "{ns}binaryDataArray/" \
            #                 "{ns}cvParam[@accession='{Acc}']/..".format(
            #                         ns=self.ns,
            #                         Acc=self.accessions['intensity array']
            #                 ),
            #     'time'    : "{ns}binaryDataArrayList/" \
            #                 "{ns}binaryDataArray/" \
            #                 "{ns}cvParam[@accession='{Acc}']/..".format(
            #                         ns=self.ns,
            #                         Acc=self.accessions['time array']
            #                 ),
            #     'float_type' : "./{ns}cvParam[@accession='{Acc}']"
            # }

        self._decode = self._decode_to_numpy
        # assign function to create numpy array to list???
        self._array = np.array

    def __repr__(self):
        return "<__main__.Chromatogram object with native ID {0} at {1}>".format(
            self.ID, hex(id(self))
        )

    def __str__(self):
        return "<__main__.Chromatogram object with native ID {0} at {1}>".format(
            self.ID, hex(id(self))
        )

    @property
    def ID(self):
        if self._ID is None:
            self._ID = self.element.get("id")
        return self._ID

    @property
    def mz(self):
        """"""
        print("Chromatogram has no property mz.\nReturn retention time instead")
        return self.time

    @property
    def time(self):
        """
        Returns the list of time values. If the time values are encoded, the
        function _decode() is used to decode the encoded data.\n
        The time property can also be set, e.g. for theoretical data.
        However, it is recommended to use the profile property to set time and
        intensity tuples at same time.

        Returns:
            time (list): list of time values from the analyzed chromatogram

        """
        if self._time is None:
            params = self._get_encoding_parameters("time array")
            self._time = self._decode(*params)
        return self._time

    @property
    def i(self):
        if self._i is None:
            params = self._get_encoding_parameters("intensity array")
            self._i = self._decode(*params)
        return self._i

    @property
    def profile(self):
        """
        Returns the list of peaks of the chromatogram as tuples (time, intensity).

        Returns:
            peaks (list): list of time, i tuples

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(
        ...     spectra.mzMl.gz,
        ...     MS_precisions = {
        ...         1 : 5e-6,
        ...         2 : 20e-6
        ...     }
        ... )
        >>> for entry in run:
        ...     if isinstance(entry, pymzml.spec.Chromatogram):
        ...         for time, intensity in entry.peaks:
        ...             print(time, intensity)

        Note:
           The peaks property can also be set, e.g. for theoretical data.
           It requires a list of time/intensity tuples.

        """
        if self._profile is None:
            if self._time is None and self._i is None:
                self._profile = []
                for pos, t in enumerate(self.time):
                    self._profile.append([t, self.i[pos]])
                    # much faster than zip ... list(zip(self.mz, self.i))
            elif self._time is not None and self._i is not None:
                self._profile = []
                for pos, t in enumerate(self.time):
                    self._profile.append([t, self.i[pos]])
            elif self._profile is None:
                self._profile = []
        return self._array(self._profile)

    @profile.setter
    def profile(self, tuple_list):
        if len(tuple_list) == 0:
            return
        # self._mz, self._i = map(list, zip(*tuple_list))
        # same here .. zip is soooooo slow :)
        self._time = []
        self._i = []
        for time, i in tuple_list:
            self._time.append(time)
            self._i.append(i)
        self._peaks = tuple_list
        self._reprofiledPeaks = None
        self._centroidedPeaks = None
        return self

    def peaks(self):
        """
        Return the list of peaks of the spectrum as tuples (time, intensity).

        Returns:
            peaks (list): list of time, intensity tuples

        Example:

        >>> import pymzml
        >>> run = pymzml.run.Reader(
        ...     spectra.mzMl.gz,
        ...     MS_precisions =  {
        ...         1 : 5e-6,
        ...         2 : 20e-6
        ...     }
        ... )
        >>> for entry in run:
        ...     if isinstance(entry, pymzml.spec.Chromatogram):
        ...         for time, intensity in entry.peaks:
        ...             print(time, intensity)

        Note:
           The peaks property can also be set, e.g. for theoretical data.
           It requires a list of time/intensity tuples.

        """
        return self.profile
