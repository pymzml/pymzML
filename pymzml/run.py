# -*- coding: utf-8 -*-
# encoding: utf-8
"""
The class :py:class:`Reader` has been designed to selectively extract data
from a mzML file and to expose the data as a python object.
Necessary information are read in and stored in a fast
accessible format.
The reader itself is an iterator, thus looping over all spectra
follows the classical pythonian syntax.
Additionally one can random access spectra by their nativeID
if the file if not truncated by a conversion Program.

Note:
    The class :py:class:`Writer` is still in development.

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
#    along with this program.  If not, see
#    <http://www.gnu.org/licenses/>


import re
import os
import xml.etree.ElementTree as ElementTree
from collections import defaultdict as ddict
from io import BytesIO

from . import spec
from . import obo
from . import regex_patterns
from .file_interface import FileInterface
from .file_classes.standardMzml import StandardMzml


class Reader(object):
    """
    Initialize Reader object for a given mzML file.

    Arguments:
        path (str): path to the mzml file to parse.

    Keyword Arguments:
        MS_precisions (dict): measured precisions for the different MS levels.
            e.g.::

                {
                    1 : 5e-6,
                    2 : 20e-6
                }

        obo_version (str, optional): obo version number as string. If not
            specified the version will be extracted from the mzML file

    Note:
        Setting the precision for MS1 and MSn spectra has changed in version 1.2.
        However, the old syntax as kwargs is still compatible ( e.g. 'MS1_Precision=5e-6').
    """

    def __init__(
        self,
        path_or_file,
        MS_precisions = None,
        obo_version   = None,
        build_index_from_scratch=False,
        skip_chromatogram=True,
        **kwargs
    ):
        """Initialize and set required attributes."""
        self.build_index_from_scratch = build_index_from_scratch
        self.skip_chromatogram = skip_chromatogram
        if MS_precisions is None:
            MS_precisions = {}
            if "MS1_Precision" in kwargs.keys():
                MS_precisions[1] = kwargs["MS1_Precision"]
            if "MSn_Precision" in kwargs.keys():
                MS_precisions[2] = kwargs["MSn_Precision"]
                MS_precisions[3] = kwargs["MSn_Precision"]

        # Parameters
        self.ms_precisions = {
            0: 0.001,  # arbitrary prec for UV spectra
            1: 5e-6,
            2: 20e-6,
        }
        self.ms_precisions.update(MS_precisions)

        # File info
        self.info                = ddict()
        if isinstance(path_or_file, str):
            self.info['file_name']   = path_or_file
            self.info['encoding']    = self._determine_file_encoding(path_or_file)
        else:
            self.info['encoding']    = self._guess_encoding(path_or_file)
            
        self.info['file_object'] = self._open_file(path_or_file)
        self.info['offset_dict'] = self.info['file_object'].offset_dict
        self.info['obo_version'] = obo_version

        self.iter = self._init_iter()
        self.OT = self._init_obo_translator()

    def __next__(self):
        """
        Iterator for the class :py:class:`Run`.

        Iterates all of the spectra in the file.

        Returns:
            Spectrum (:py:class:`Spectrum`): a spectrum object with interface
                to the original spectrum element.

        Example:

        >>> for spectrum in Reader:
        ...     print(spectrum.mz, end='\\r')

        """
        has_ref_group = self.info.get("referenceable_param_group_list", False)
        while True:
            event, element = next(self.iter, ("END", "END"))
            if event == "end":
                if element.tag.endswith("}spectrum"):
                    spectrum = spec.Spectrum(element)
                    if has_ref_group:
                        spectrum._set_params_from_reference_group(
                            self.info["referenceable_param_group_list_element"]
                        )
                    ms_level = spectrum.ms_level
                    spectrum.measured_precision = self.ms_precisions[ms_level]
                    spectrum.calling_instance = self
                    return spectrum
                if element.tag.endswith("}chromatogram"):
                    if self.skip_chromatogram:
                        continue
                    spectrum = spec.Chromatogram(element)
                    # if has_ref_group:
                    #     spectrum._set_params_from_reference_group(
                    #         self.info['referenceable_param_group_list_element']
                    #     )
                    spectrum.calling_instance = self
                    return spectrum
            elif event == "END":
                raise StopIteration

    def __getitem__(self, identifier):
        """
        Access spectrum with native id 'identifier'.

        Arguments:
            identifier (str or int): last number in the id tag of the spectrum
                element

        Returns:
            spectrum (Spectrum or Chromatogram): spectrum/chromatogram object
            with native id 'identifier'
        """
        spectrum = self.info["file_object"][identifier]
        spectrum.calling_instance = self
        if isinstance(spectrum, spec.Spectrum):
            spectrum.measured_precision = self.ms_precisions[spectrum.ms_level]
        return spectrum

    @property
    def file_class(self):
        """Return file object in use."""
        return type(self.info["file_object"].file_handler)

    def _open_file(self, path_or_file):
        """
        Open the path using the FileInterface class as a wrapper.

        Arguments:
            path (str): path to the file to parse

        Returns:
            (FileInterface): Wrapper class for compressed and uncompressed
                mzml files
        """
        return FileInterface(
            path_or_file,
            self.info['encoding'],
            build_index_from_scratch=self.build_index_from_scratch
        )

    def _guess_encoding(self, mzml_file):
        """
        Determine the encoding used for the file.

        Arguments:
            mzml_file (IOBase): an mzml file

        Returns:
            mzml_encoding (str): encoding type of the file
        """
        match = regex_patterns.FILE_ENCODING_PATTERN.search(mzml_file.readline())
        if match:
            return bytes.decode(match.group('encoding'))
        else:
            return 'utf-8'

    def _determine_file_encoding(self, path):
        """
        Determine the encoding used for the file in path.

        Arguments:
            path (str): path to the mzml files

        Returns:
            mzml_encoding (str): encoding type of the file
        """
        if os.path.exists(path):
            print(path)
            if path.endswith('.gz') or path.endswith('.igz'):
                import gzip
                _open = gzip.open
            else:
                _open = open
            with _open(path, 'rb') as sniffer:
                return self._guess_encoding(sniffer)

    def _init_obo_translator(self):
        """
        Initialize the obo translator with the minimum requirement
        and extra Accessions.

        Returns:
            obo_translator (OboTranslator): translator class to translate
                accessions to names
        """
        # parse obo, check MS tags and if they are ok in minimum.py (minimum
        # required) ...
        if self.info.get("obo_version", None) is None:
            self.info["obo_version"] = "1.1.0"
        obo_translator = obo.OboTranslator(version=self.info["obo_version"])

        return obo_translator

    def _init_iter(self):
        """
        Initalize the iterator for the spectra and sets it to the start
        of the spectrumList element.

        Returns:
            mzml_iter (xml.etree.ElementTree._IterParseIterator): Iterator over
                all element in the file starting with the first spectrum
        """
        mzml_iter = iter(
            ElementTree.iterparse(self.info["file_object"], events=("end", "start"))
        )  # NOTE: end might be sufficient
        _, self.root = next(mzml_iter)
        while True:
            event, element = next(mzml_iter, ("END", "END"))
            if element.tag.endswith("}mzML"):
                if "version" in element.attrib and len(element.attrib["version"]) > 0:
                    self.info["mzml_version"] = element.attrib["version"]
                else:
                    s = element.attrib[
                        "{http://www.w3.org/2001/XMLSchema-instance}" "schemaLocation"
                    ]
                    self.info["mzml_version"] = re.search(
                        r"[0-9]*\.[0-9]*\.[0-9]*", s
                    ).group()
            elif element.tag.endswith("}cv"):
                if (
                    not self.info["obo_version"]
                    and element.attrib.get("id", None) == "MS"
                ):
                    self.info["obo_version"] = element.attrib.get("version", "1.1.0")
            elif element.tag.endswith("}referenceableParamGroupList"):
                self.info["referenceable_param_group_list"] = True
                self.info["referenceable_param_group_list_element"] = element
            elif element.tag.endswith("}spectrumList"):
                spec_cnt = element.attrib.get("count")
                self.info["spectrum_count"] = int(spec_cnt) if spec_cnt else None
                break
            elif element.tag.endswith("}chromatogramList"):
                chrom_cnt = element.attrib.get("count", None)
                if chrom_cnt is None:
                    self.info["chromatogram_count"] = None
                else:
                    self.info["chromatogram_count"] = int(chrom_cnt)
                break
            elif element.tag.endswith("}run"):
                run_id = element.attrib.get("id")
                start_time = element.attrib.get("startTimeStamp")
                self.info["run_id"] = run_id
                self.info["start_time"] = start_time
            else:
                pass
        self.root.clear()
        return mzml_iter

    def __iter__(self):
        """Return self."""
        return self

    def next(self):
        """Function to return the next Spectrum element."""
        return self.__next__()

    def get_spectrum_count(self):
        """
        Number of spectra in file.

        Returns:
            spectrum count (int): Number of spectra in file.
        """
        return self.info["spectrum_count"]

    def get_chromatogram_count(self):
        """
        Number of chromatograms in file.

        Returns:
            chromatogram count (int): Number of chromatograms in file.
        """
        return self.info["chromatogram_count"]


if __name__ == "__main__":
    print(__doc__)
