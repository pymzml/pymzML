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
import os
import math
import xml.etree.ElementTree as ElementTree
from collections import defaultdict as ddict
from io import BytesIO
from pathlib import Path

from . import spec
from . import chromatogram
from . import obo
from . import regex_patterns
from .file_interface import FileInterface
from .file_classes.standardMzml import StandardMzml

from logging import getLogger

logger = getLogger(__name__)

DEFAULT_OBO_VERSION = "4.1.79"


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
        MS_precisions=None,
        obo_version=None,
        build_index_from_scratch=False,
        skip_chromatogram=True,
        index_regex=None,
        **kwargs,
    ):
        """Initialize and set required attributes."""
        self.index_regex = index_regex
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
            None: 0.0001,  # if spectra does not contain ms_level information
            # e.g. UV-chromatograms (thanks pyeguy) then ms_level is
            # returned as None
            0: 0.0001,
            1: 5e-6,
            2: 20e-6,
            3: 20e-6,
        }
        self.ms_precisions.update(MS_precisions)

        # File info
        self.info = ddict()
        self.path_or_file = path_or_file
        self._retention_time_index = None
        if isinstance(self.path_or_file, Path):
            self.path_or_file = str(self.path_or_file)
        if isinstance(self.path_or_file, str):
            self.info["file_name"] = self.path_or_file
            self.info["encoding"] = self._determine_file_encoding(self.path_or_file)
        else:
            self.info["encoding"] = self._guess_encoding(self.path_or_file)

        self.info["file_object"] = self._open_file(
            self.path_or_file, build_index_from_scratch=self.build_index_from_scratch
        )
        self.info["offset_dict"] = self.info["file_object"].offset_dict
        if obo_version:
            self.info["obo_version"] = self._obo_version_validator(obo_version)
            self.OT = self._init_obo_translator()
        else:
            # obo version not specified -> identified from mzML by self._init_iter
            self.info["obo_version"] = None
            self.OT = None

        self.iter = self._init_iter()

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
                    spectrum = spec.Spectrum(element, obo_version=self.OT.version)
                    if has_ref_group:
                        spectrum._set_params_from_reference_group(
                            self.info["referenceable_param_group_list_element"]
                        )
                    ms_level = spectrum.ms_level
                    spectrum.measured_precision = self.ms_precisions[ms_level]
                    return spectrum
                if element.tag.endswith("}chromatogram"):
                    if self.skip_chromatogram:
                        continue
                    spectrum = chromatogram.Chromatogram(
                        element, obo_version=self.OT.version
                    )
                    # if has_ref_group:
                    #     spectrum._set_params_from_reference_group(
                    #         self.info['referenceable_param_group_list_element']
                    #     )
                    return spectrum
            elif event == "END":
                # reinit iter
                self.info["file_object"].close()
                self.info["file_object"] = self._open_file(
                    self.path_or_file, build_index_from_scratch=False
                )
                self.iter = self._init_iter()
                raise StopIteration

    def __getitem__(self, identifier):
        """
        Access spectrum or chromatogram with native id 'identifier'.

        Arguments:
            identifier (str or int): last number in the id tag of the spectrum
                element or a chromatogram identifier like 'TIC'

        Returns:
            spectrum (Spectrum or Chromatogram): spectrum/chromatogram object
            with native id 'identifier'
        """
        element = self.info["file_object"][identifier]
        element.obo_translator = self.OT

        if isinstance(element, spec.Spectrum):
            element.measured_precision = self.ms_precisions[element.ms_level]

        return element

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def file_class(self):
        """Return file object in use."""
        return type(self.info["file_object"].file_handler)

    def _open_file(self, path_or_file, build_index_from_scratch=False):
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
            self.info["encoding"],
            build_index_from_scratch=build_index_from_scratch,
            index_regex=self.index_regex,
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
            return bytes.decode(match.group("encoding"))
        else:
            return "utf-8"

    def _determine_file_encoding(self, path):
        """
        Determine the encoding used for the file in path.

        Arguments:
            path (str): path to the mzml files

        Returns:
            mzml_encoding (str): encoding type of the file
        """
        if os.path.exists(path):
            if path.endswith(".gz") or path.endswith(".igz"):
                import gzip

                _open = gzip.open
            else:
                _open = open
            with _open(path, "rb") as sniffer:
                return self._guess_encoding(sniffer)

    @staticmethod
    def _obo_version_validator(version):
        """
        The obo version should fit file names in the obo folder.
        However, some software generate mzML with built in obo version string like:
        '23:06:2017' or even newer version that not in obo folder yet.
        This is to check obo version and try to fit the best obo version
        to the obo version in the mzML file.

        Arguments:
            version (str): The original version to check.

        Returns:
            version_fixed (str): The checked obo version.
        """
        obo_rgx = re.compile(r"(\d\.\d{1,2}\.\d{1,2})(_[rR][cC]\d{0,2})?")
        obo_years_rgx = re.compile(r"20\d\d")
        obo_year_version_dct = {
            2012: "3.40.0",
            2013: "3.50.0",
            2014: "3.60.0",
            2015: "3.75.0",
            2016: "4.0.1",
            2017: "4.1.0",
            2018: "4.1.10",
            2019: "4.1.22",
            2024: "4.1.79",
            2025: "4.1.188",
        }
        version_fixed = None
        if obo_rgx.match(version):
            version_fixed = version
        else:
            if obo_years_rgx.search(version):
                years_found = obo_years_rgx.search(version)
                if years_found:
                    try:
                        year = int(years_found.group(0))
                    except ValueError:
                        year = 2000

                    if year in obo_year_version_dct:
                        version_fixed = obo_year_version_dct[year]
                    else:
                        if year > 2019:
                            version_fixed = "4.1.0"

        if version_fixed:
            # Check if the corresponding obo file existed in obo folder
            obo_root = os.path.dirname(__file__)
            obo_file = os.path.join(
                obo_root,
                "obo",
                "psi-ms{0}.obo".format("-" + version_fixed if version_fixed else ""),
            )
            if not (os.path.exists(obo_file) or os.path.exists(obo_file + ".gz")):
                version_fixed = DEFAULT_OBO_VERSION
        else:
            version_fixed = DEFAULT_OBO_VERSION

        return version_fixed

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
            self.info["obo_version"] = DEFAULT_OBO_VERSION
        obo_translator = obo.OboTranslator.from_cache(version=self.info["obo_version"])

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
        self.info["chromatogram_count"] = None
        self.info["spectrum_count"] = None
        while True:
            event, element = next(mzml_iter, ("END", "END"))
            if element.tag.endswith("}mzML"):
                if "version" in element.attrib and len(element.attrib["version"]) > 0:
                    self.info["mzml_version"] = element.attrib["version"]
                else:
                    s = element.attrib[
                        "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"
                    ]
                    self.info["mzml_version"] = re.search(
                        r"[0-9]*\.[0-9]*\.[0-9]*", s
                    ).group()
            elif element.tag.endswith("}cv"):
                if (
                    not self.info["obo_version"]
                    and element.attrib.get("id", None) == "MS"
                ):
                    obo_in_mzml = element.attrib.get("version", DEFAULT_OBO_VERSION)
                    self.info["obo_version"] = self._obo_version_validator(obo_in_mzml)
                    self.OT = self._init_obo_translator()

            elif element.tag.endswith("}fileDescription"):
                self.info["file_description"] = True
                self.info["file_description_element"] = element
            elif element.tag.endswith("}sampleList"):
                self.info["sample_list"] = True
                self.info["sample_list_element"] = element

            elif element.tag.endswith("}referenceableParamGroupList"):
                self.info["referenceable_param_group_list"] = True
                self.info["referenceable_param_group_list_element"] = element

            elif element.tag.endswith("}softwareList"):
                self.info["software_list"] = True
                self.info["software_list_element"] = element
            elif element.tag.endswith("}instrumentConfigurationList"):
                self.info["instrument_configuration_list"] = True
                self.info["instrument_configuration_list_element"] = element
            elif element.tag.endswith("}dataProcessingList"):
                self.info["data_processing_list"] = True
                self.info["data_processing_list_element"] = element
            elif element.tag.endswith("}cvParam"):
                if self.term_is_a_member(element.attrib.get("accession"), "MS:1000494"):
                    self.info["instrument_name"] = element.attrib.get("name")

            elif element.tag.endswith("}spectrumList"):
                spec_cnt = element.attrib.get("count")
                self.info["spectrum_count"] = int(spec_cnt) if spec_cnt else None
                break
            elif element.tag.endswith("}chromatogramList"):
                chrom_cnt = element.attrib.get("count", None)
                if chrom_cnt:
                    self.info["chromatogram_count"] = int(chrom_cnt)
                break
            elif element.tag.endswith("}run"):
                run_id = element.attrib.get("id")
                start_time = element.attrib.get("startTimeStamp")
                self.info["run_element"] = element
                self.info["run_id"] = run_id
                self.info["start_time"] = start_time
            else:
                pass
        if self.OT is None:
            # no MS cv in mzML -> default obo
            self.OT = self._init_obo_translator()
        self.root.clear()
        return mzml_iter

    def __iter__(self):
        """Return self."""
        return self

    def next(self):
        """Function to return the next Spectrum element."""
        return self.__next__()

    def iter_spectra(self, ms_level=None, rt_range=None, polarity=None):
        """Iterate over spectra matching optional filters.

        Filtering is lazy and starts at the Reader's current position.

        Args:
            ms_level (int, optional): MS level to include.
            rt_range (tuple, optional): Inclusive retention-time range in minutes.
                Either boundary may be ``None``.
            polarity (str, optional): ``"positive"`` or ``"negative"``.

        Yields:
            Spectrum: Each matching spectrum.
        """
        polarity = self._normalize_polarity(polarity)
        rt_range = self._normalize_rt_range(rt_range)

        for spectrum in self:
            if self._spectrum_matches_filters(
                spectrum, ms_level, rt_range, polarity
            ):
                yield spectrum

    @staticmethod
    def _normalize_polarity(polarity):
        """Return a validated, lower-case polarity filter."""
        if polarity is None:
            return None
        if not isinstance(polarity, str):
            raise ValueError("polarity must be 'positive' or 'negative'")

        polarity = polarity.lower()
        if polarity not in {"positive", "negative"}:
            raise ValueError("polarity must be 'positive' or 'negative'")
        return polarity

    @staticmethod
    def _normalize_rt_range(rt_range):
        """Return a validated retention-time range."""
        if rt_range is None:
            return None
        if len(rt_range) != 2:
            raise ValueError("rt_range must contain two boundaries")
        return rt_range

    @staticmethod
    def _spectrum_matches_filters(spectrum, ms_level, rt_range, polarity):
        """Return whether a spectrum satisfies the requested filters."""
        if not isinstance(spectrum, spec.Spectrum):
            return False
        if ms_level is not None and spectrum.ms_level != ms_level:
            return False
        if polarity is not None and spectrum[f"{polarity} scan"] is None:
            return False
        if rt_range is None:
            return True

        scan_time = spectrum.scan_time_in_minutes()
        if scan_time is None:
            return False
        lower_bound, upper_bound = rt_range
        return (
            (lower_bound is None or scan_time >= lower_bound)
            and (upper_bound is None or scan_time <= upper_bound)
        )

    def extract_xic(
        self,
        mz,
        tolerance=10.0,
        unit="ppm",
        rt_range=None,
        ms_level=1,
    ):
        """Extract an ion chromatogram for a target m/z.

        Args:
            mz (float): Target mass-to-charge value.
            tolerance (float): Symmetric matching tolerance.
            unit (str): ``"ppm"`` or ``"Da"``.
            rt_range (tuple, optional): Inclusive retention-time range in minutes.
            ms_level (int, optional): MS level to use. Defaults to MS1.

        Returns:
            Chromatogram: Extracted time and summed-intensity values.

        A point is retained for every matching spectrum, including spectra with
        no signal inside the requested m/z window.
        """
        mz = float(mz)
        tolerance = float(tolerance)
        if tolerance < 0:
            raise ValueError("tolerance must not be negative")

        unit = unit.lower()
        if unit not in {"ppm", "da"}:
            raise ValueError("unit must be 'ppm' or 'Da'")
        mass_window = mz * tolerance * 1e-6 if unit == "ppm" else tolerance

        profile = []
        for spectrum in self.iter_spectra(ms_level=ms_level, rt_range=rt_range):
            peaks = spectrum.peaks("raw")
            matches = abs(peaks[:, 0] - mz) <= mass_window
            intensity = float(peaks[matches, 1].sum())
            profile.append((spectrum.scan_time_in_minutes(), intensity))

        xic_id = f"XIC {mz}"
        namespace = "{http://psi.hupo.org/ms/mzml}"
        element = ElementTree.Element(f"{namespace}chromatogram", id=xic_id)
        # Use the standard CV term so the result behaves like a chromatogram
        # read from an mzML file, not a special in-memory variant.
        ElementTree.SubElement(
            element,
            f"{namespace}cvParam",
            cvRef="MS",
            accession="MS:1000627",
            name="selected ion current chromatogram",
        )
        xic = chromatogram.Chromatogram(element, obo_version=self.OT.version)
        xic.profile = profile
        return xic

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

    def get_spectrum(self, identifier):
        """
        Access spectrum with the given identifier.

        Arguments:
            identifier (str or int): Either a string identifier or an index (0-based)
                to access spectra in order.

        Returns:
            spectrum (Spectrum): spectrum object with the given identifier

        Note:
            This method provides the same functionality as using the indexing syntax
            (e.g., run[0]), but with a more explicit method name.
        """
        return self[identifier]

    def get_spectrum_at_time(self, time, ms_level=None):
        """Return the spectrum nearest to a retention time in minutes.

        The time index is built on first use and then reused. Looking up a
        spectrum does not move this reader's current iteration position.

        Args:
            time (float): Retention time in minutes.
            ms_level (int, optional): Only consider spectra at this MS level.

        Returns:
            Spectrum: The closest matching spectrum. If two spectra are equally
            close, the earlier one is returned.

        Raises:
            ValueError: If ``time`` is not a finite number.
            LookupError: If the file has no spectra matching ``ms_level``.
        """
        requested_time = self._normalize_requested_time(time)

        first_lookup = self._retention_time_index is None
        closest_spectrum = (
            self._build_retention_time_index(requested_time, ms_level)
            if first_lookup
            else None
        )

        matches = [
            entry
            for entry in self._retention_time_index
            if ms_level is None or entry[2] == ms_level
        ]
        if not matches:
            detail = "" if ms_level is None else f" at MS level {ms_level}"
            raise LookupError(f"No spectra with retention times were found{detail}")

        nearest = min(
            matches,
            key=lambda entry: self._time_distance_key(entry[0], requested_time),
        )
        if first_lookup and closest_spectrum.ID == nearest[1]:
            return closest_spectrum

        with self._new_lookup_reader() as lookup_reader:
            return lookup_reader[nearest[1]]

    @staticmethod
    def _normalize_requested_time(time):
        """Return a finite retention time in minutes."""
        try:
            requested_time = float(time)
        except (TypeError, ValueError) as error:
            raise ValueError("time must be a finite number of minutes") from error
        if not math.isfinite(requested_time):
            raise ValueError("time must be a finite number of minutes")
        return requested_time

    def _build_retention_time_index(self, requested_time, ms_level):
        """Build the time index and retain the closest spectrum from the scan."""
        self._retention_time_index = []
        closest_spectrum = None
        with self._new_lookup_reader() as lookup_reader:
            for spectrum in lookup_reader:
                if not isinstance(spectrum, spec.Spectrum):
                    continue
                retention_time = spectrum.scan_time_in_minutes()
                if retention_time is None:
                    continue
                self._retention_time_index.append(
                    (retention_time, spectrum.ID, spectrum.ms_level)
                )
                if self._is_better_time_match(
                    spectrum, closest_spectrum, requested_time, ms_level
                ):
                    closest_spectrum = spectrum

        self._retention_time_index.sort(key=lambda entry: entry[0])
        return closest_spectrum

    @classmethod
    def _is_better_time_match(
        cls, spectrum, closest_spectrum, requested_time, ms_level
    ):
        """Return whether a spectrum is the best matching candidate so far."""
        if ms_level is not None and spectrum.ms_level != ms_level:
            return False
        if closest_spectrum is None:
            return True
        return cls._time_distance_key(
            spectrum.scan_time_in_minutes(), requested_time
        ) < cls._time_distance_key(
            closest_spectrum.scan_time_in_minutes(), requested_time
        )

    @staticmethod
    def _time_distance_key(retention_time, requested_time):
        """Sort by distance, then prefer the earlier spectrum."""
        return (abs(retention_time - requested_time), retention_time)

    def _new_lookup_reader(self):
        """Open an independent reader so a lookup cannot disturb iteration."""
        source = self.path_or_file
        if isinstance(source, BytesIO):
            source = BytesIO(source.getvalue())
        return type(self)(
            source,
            MS_precisions=self.ms_precisions,
            obo_version=self.info["obo_version"],
            skip_chromatogram=True,
            index_regex=self.index_regex,
        )

    def get_chromatogram(self, identifier):
        """
        Access chromatogram with the given identifier.

        Arguments:
            identifier (str or int): Either a string identifier like 'TIC' or
                an index (0-based) to access chromatograms in order.

        Returns:
            chromatogram (Chromatogram): chromatogram object with the given identifier

        Note:
            This method is only useful when skip_chromatogram is set to False
            if you want to access chromatograms by index. If skip_chromatogram is True,
            you can still access chromatograms by string identifiers (e.g., 'TIC').
        """
        if isinstance(identifier, str):
            return self[identifier]

        if isinstance(identifier, int):
            if self.get_chromatogram_count() is None:
                raise Exception("No chromatograms found in the file")

            if identifier >= self.get_chromatogram_count():
                raise Exception(
                    f"Chromatogram index {identifier} is out of range (0-{self.get_chromatogram_count() - 1})"
                )

            # Reset the file pointer and iterate to find the chromatogram
            temp_skip_chromatogram = self.skip_chromatogram
            self.skip_chromatogram = False

            self.info["file_object"].close()
            self.info["file_object"] = self._open_file(
                self.path_or_file, build_index_from_scratch=False
            )
            self.iter = self._init_iter()

            chrom_count = 0
            try:
                for element in self:
                    if isinstance(element, chromatogram.Chromatogram):
                        if chrom_count == identifier:
                            return element
                        chrom_count += 1
            finally:
                # Restore original skip_chromatogram setting
                self.skip_chromatogram = temp_skip_chromatogram

            raise Exception(f"Chromatogram with index {identifier} not found")

        raise ValueError("Identifier must be a string or an integer")

    def close(self):
        self.info["file_object"].close()

    def __del__(self):
        try:
            self.close()
        except (AttributeError, KeyError):
            pass

    def term_is_a_member(self, tested_term, member_of_term):
        """
        Use translated obo file to check if given term is_a member of the

        Returns:
            is_member (bool) whether given term is a member of member_of_term

        """
        is_member = False
        if self.OT is None:
            # cvParam before any MS cv -> default obo
            self.OT = self._init_obo_translator()
        try:
            term_in = self.OT[tested_term]
            if term_in:
                is_member = self.OT.id[tested_term]["is_a"].startswith(member_of_term)
        except KeyError:
            logger.warning(f"term not found ({tested_term})")
        return is_member


if __name__ == "__main__":
    print(__doc__)
