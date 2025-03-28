#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
The chromatogram class offers a python object for mass spectrometry chromatogram data.
The chromatogram object holds the basic information of the chromatogram and offers
methods to interrogate properties of the chromatogram.
Data, i.e. time and intensity decoding is performed on demand
and can be accessed via their properties, e.g. :py:attr:`~pymzml.chromatogram.Chromatogram.peaks`.

The Chromatogram class is used in the :py:class:`~pymzml.run.Reader` class.
There each chromatogram is accessible as a chromatogram object.
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

import re
import numpy as np
from .msdata import MsData
from .obo import OboTranslator


class Chromatogram(MsData):
    """
    Class for Chromatogram access and handling.
    """

    def __init__(self, element, measured_precision=5e-6, *, obo_version=None):
        """
        Arguments:
            element (xml.etree.ElementTree.Element): chromatogram as xml Element

        Keyword Arguments:
            measured_precision (float): in ppm, i.e. 5e-6 equals to 5 ppm.
            obo_version (str, optional): obo version number.
        """
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
        self._chromatogram_type = None
        self._precursor_mz = None
        self._product_mz = None
        self._polarity = None
        self.obo_translator = OboTranslator.from_cache(obo_version)

        if self.element:
            self.ns = (
                re.match(r"\{.*\}", element.tag).group(0)
                if re.match(r"\{.*\}", element.tag)
                else ""
            )

        self._decode = self._decode_to_numpy
        # assign function to create numpy array to list???
        self._array = np.array

    def __repr__(self):
        """
        Returns representative string for a chromatogram object class
        """
        return "<__main__.Chromatogram object with native ID {0} at {1}>".format(
            self.ID, hex(id(self))
        )

    def __str__(self):
        """
        Returns representative string for a chromatogram object class
        """
        return "<__main__.Chromatogram object with native ID {0} at {1}>".format(
            self.ID, hex(id(self))
        )

    @property
    def ID(self):
        """
        Access the native id of the chromatogram.

        Returns:
            ID (str): native ID of the chromatogram
        """
        if self._ID is None:
            if self.element:
                self._ID = self.element.get("id")
        return self._ID

    @property
    def mz(self):
        """
        Chromatogram has no property mz. This property is included for
        compatibility with the Spectrum class.

        Returns:
            time (list): list of time values from the chromatogram
        """
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
        """
        Returns the list of intensity values from the analyzed chromatogram.

        Returns:
            i (list): list of intensity values from the analyzed chromatogram
        """
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
        ...     if isinstance(entry, pymzml.chromatogram.Chromatogram):
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
        """
        Set the chromatogram profile.

        Args:
            tuple_list (list): list of tuples (time, intensity)
        """
        if len(tuple_list) == 0:
            return
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
        Return the list of peaks of the chromatogram as tuples (time, intensity).

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
        ...     if isinstance(entry, pymzml.chromatogram.Chromatogram):
        ...         for time, intensity in entry.peaks:
        ...             print(time, intensity)

        Note:
           The peaks property can also be set, e.g. for theoretical data.
           It requires a list of time/intensity tuples.

        """
        return self.profile

    @property
    def chromatogram_type(self):
        """
        Returns the chromatogram type.

        Returns:
            chromatogram_type (str): chromatogram type
        """
        if self._chromatogram_type is None:
            for element in self.element.iter():
                if element.tag.endswith("}cvParam"):
                    accession = element.get("accession")
                    # Check for chromatogram type accessions
                    if accession in [
                        "MS:1000235",  # total ion current chromatogram
                        "MS:1000627",  # selected ion current chromatogram
                        "MS:1000628",  # basepeak intensity chromatogram
                        "MS:1000810",  # chromatogram
                        "MS:1000811",  # chromatogram created by spectrum aggregation
                        "MS:1000812",  # single ion monitoring chromatogram
                        "MS:1000813",  # multiple reaction monitoring chromatogram
                        "MS:1000814",  # selected reaction monitoring chromatogram
                        "MS:1000815",  # consecutive reaction monitoring chromatogram
                        "MS:1001472",  # selected ion monitoring chromatogram
                        "MS:1001473",  # selected reaction monitoring chromatogram
                        "MS:1001474",  # consecutive reaction monitoring chromatogram
                        "MS:1001475",  # targeted SIM chromatogram
                        "MS:1001476",  # automatic SIM chromatogram
                        "MS:1001477",  # targeted SRM chromatogram
                        "MS:1001478",  # automatic SRM chromatogram
                        "MS:1001479",  # targeted CRM chromatogram
                        "MS:1001480",  # automatic CRM chromatogram
                    ]:
                        self._chromatogram_type = element.get("name")
                        break
        return self._chromatogram_type

    @property
    def polarity(self):
        """
        Returns the polarity of the chromatogram.

        Returns:
            polarity (str): polarity (positive scan or negative scan)
        """
        if self._polarity is None:
            for element in self.element.iter():
                if element.tag.endswith("}cvParam"):
                    accession = element.get("accession")
                    # Check for polarity accessions
                    if accession in [
                        "MS:1000129",  # negative scan
                        "MS:1000130",  # positive scan
                    ]:
                        self._polarity = element.get("name")
                        break
        return self._polarity

    @property
    def precursor_mz(self):
        """
        Returns the precursor m/z value for SRM/MRM chromatograms.

        Returns:
            precursor_mz (float): precursor m/z value
        """
        if self._precursor_mz is None:
            precursor = self.element.find(f".//{self.ns}precursor")
            if precursor is not None:
                isolation_window = precursor.find(f".//{self.ns}isolationWindow")
                if isolation_window is not None:
                    for element in isolation_window.iter():
                        if (
                            element.tag.endswith("}cvParam")
                            and element.get("accession") == "MS:1000827"
                        ):  # isolation window target m/z
                            self._precursor_mz = float(element.get("value"))
                            break
        return self._precursor_mz

    @property
    def product_mz(self):
        """
        Returns the product m/z value for SRM/MRM chromatograms.

        Returns:
            product_mz (float): product m/z value
        """
        if self._product_mz is None:
            product = self.element.find(f".//{self.ns}product")
            if product is not None:
                isolation_window = product.find(f".//{self.ns}isolationWindow")
                if isolation_window is not None:
                    for element in isolation_window.iter():
                        if (
                            element.tag.endswith("}cvParam")
                            and element.get("accession") == "MS:1000827"
                        ):  # isolation window target m/z
                            self._product_mz = float(element.get("value"))
                            break
        return self._product_mz

    def get_chromatogram_properties(self):
        """
        Returns a dictionary with the main properties of the chromatogram.

        Returns:
            properties (dict): dictionary with chromatogram properties
        """
        properties = {
            "id": self.ID,
            "chromatogram_type": self.chromatogram_type,
            "polarity": self.polarity,
            "precursor_mz": self.precursor_mz,
            "product_mz": self.product_mz,
        }
        return properties
