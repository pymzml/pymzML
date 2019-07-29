#!/usr/bin/env python
"""
Additional functions for converting file etc.

@author M. Kösters
"""
from pymzml.utils.GSGW import GSGW
import pymzml.regex_patterns as regex_patterns
import re
import gzip


def index_gzip(pathIn, pathOut, max_idx=10000, idx_len=8, verbose=False, comp_str=-1):
    """
    Convert an mzml file (can be gzipped) into an indexed, gzipped mzML file.

    Arguments:
        pathIn (str): path to an mzML input File.
        pathOut (str): path were the index gzip will be created.

    Keyword Arguments:
        max_idx (int): number of indexes which can be saved.
        idx_len (int): character len of on key
        verbose (boolean): print progress while parsing input.
        comp_str(int): compression strength of zlib compression,
            needs to  be 1 <= x <= 9
    """
    if pathIn.endswith("gz"):
        fileOpen = gzip.open
    elif pathIn.lower().endswith("mzml"):
        fileOpen = open
    with GSGW(
        output_path=pathOut,
        max_idx=max_idx,
        max_idx_len=idx_len,
        max_offset_len=idx_len,
        comp_str=comp_str,
    ) as Writer:
        with fileOpen(pathIn, "rt") as Reader:
            data = ""
            for line in Reader:
                if line.strip().startswith("</spectrum>"):
                    data += line
                    Writer.add_data(data, nativeID)
                    if verbose:
                        print("NativeID : {0}".format(nativeID), end="\r")
                    data = ""
                elif line.strip().startswith("<spectrum "):
                    data += line
                    lineID = re.search(regex_patterns.SPECTRUM_TAG_PATTERN, line).group(
                        "index"
                    )
                    nativeID = int(
                        regex_patterns.SPECTRUM_ID_PATTERN.search(lineID).group(1)
                    )

                elif line.strip().startswith("<chromatogram "):
                    data += line
                    nativeID = re.search(
                        regex_patterns.CHROMATOGRAM_ID_PATTERN, line
                    ).group(1)
                    print("found chromatogram")
                elif line.strip().startswith("<spectrumL"):
                    data += line
                    Writer.add_data(data, "Head")
                    if verbose:
                        print("NativeID :", "Head")
                    data = ""
                elif line.strip().startswith("<chromatogramL"):
                    data += line
                    Writer.add_data(data, "junk")
                    if verbose:
                        print("NativeID :", "junk")
                    data = ""
                elif line.strip().startswith("</chromatogram>"):
                    data += line
                    Writer.add_data(data, nativeID)
                    if verbose:
                        print("found chromatogram")
                        print("NativeID: {0}".format(nativeID))
                    data = ""
                else:
                    data += line
            if data:
                Writer.add_data(data, "tail")
                if verbose:
                    print("NativeID :", "tail")
        # print(Writer.index.items())
        Writer.write_index()
    return


def index(pathIn, pathOut, max_idx=10000, idx_len=8, verbose=False, comp_str=-1):
    """
    Convert an mzml file (can be gzipped) into an indexed, gzipped mzML file.

    Arguments:
        pathIn (str): path to input File.
        pathOut (str): path were output should be created.

    Keyword Arguments:
        max_idx (int): number of indexes which can be saved.
        idx_len (int): character len of on key
        verbose (boolean): print progress while parsing input.
        comp_str(int): compression strength of zlib compression,
            needs to  be 1 <= x <= 9
    """
    import gzip

    with GSGW(
        output_path=pathOut,
        max_idx_len=idx_len,
        max_offset_len=idx_len,
        comp_str=comp_str,
    ) as Writer:
        with gzip.open(pathIn, "rt") as Reader:
            data = ""
            for line in Reader:
                if line.strip().startswith("</spectrum>"):
                    data += line
                    Writer.add_data(data, nativeID)
                    if verbose:
                        pass
                    data = ""
                elif line.strip().startswith("<spectrum "):
                    data += line
                    lineID = re.search(regex_patterns.SPECTRUM_TAG_PATTERN, line).group(
                        "index"
                    )
                    nativeID = int(
                        regex_patterns.SPECTRUM_ID_PATTERN.search(lineID).group(0)
                    )
                elif line.strip().startswith("<chromatogram "):
                    data += line
                    nativeID = re.search(
                        regex_patterns.CHROMATOGRAM_ID_PATTERN, line
                    ).group(1)
                elif line.strip().startswith("<spectrumL"):
                    data += line
                    Writer.add_data(data, "Head")
                    if verbose:
                        print("NativeID :", "Head")
                    data = ""
                elif line.strip().startswith("<chromatogramL"):
                    data += line
                    Writer.add_data(data, "junk")
                    if verbose:
                        print("NativeID :", "junk")
                    data = ""
                elif line.strip().startswith("</chromatogram>"):
                    data += line
                    Writer.add_data(data, nativeID)
                    if verbose:
                        print("found chromo")
                        print("NativeID :", nativeID, end="\r")
                    data = ""
                else:
                    data += line
            if data:
                Writer.add_data(data, "tail")
                if verbose:
                    print("NativeID :", "tail")
        Writer.write_index()


def make_obo_mapping(obo, reversed=False):
    # NOT sure what this is for ...
    mapping = {}
    with open(obo) as obo_file:
        for line in obo_file:
            if line.startswith("id: "):
                id = line.split()[-1]
            elif line.startswith("name: "):
                mapping[id] = " ".join(line.split()[1:])
    if reversed:
        mapping = {y: x for x, y in mapping.items()}
    return mapping


if __name__ == "__main__":
    print(__doc__)
