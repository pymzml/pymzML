#!/usr/bin/env python

from __future__ import print_function
import pymzml
import os
from operator import itemgetter

def main():
    """
    Extract the 10 most often fragmented precursors from the BSA example file.

    This can e.g. be used for defining exclusion lists for further MS runs.
    
    usage:

        ./get_precursors.py

    """

    example_file = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'tests',
        'data',
        'BSA1.mzML.gz'
    )
    run = pymzml.run.Reader(example_file)
    fragmented_precursors = {}
    for spectrum in run:
        if spectrum.ms_level == 2:
            selected_precursors = spectrum.selected_precursors
            if spectrum.selected_precursors is not None:
                for precursor_mz, precursor_intensity in selected_precursors:
                    rounded_precursor_mz = round(precursor_mz,3)
                    if rounded_precursor_mz not in fragmented_precursors.keys():
                        fragmented_precursors[rounded_precursor_mz] = []
                    fragmented_precursors[rounded_precursor_mz].append(spectrum.ID) 
    
    precursor_info_list = []
    for rounded_precursor_mz, spectra_list in fragmented_precursors.items():
        precursor_info_list.append(
            (
                len(spectra_list),
                rounded_precursor_mz,
                spectra_list
            ) 
        )


    for pos, (number_of_spectra, rounded_precursor_mz, spectra_list) in enumerate(sorted(precursor_info_list, reverse=True)):
        print(
            'Found precursor: {0} in spectra: {1}'.format(
                rounded_precursor_mz,
                spectra_list
            )
        )
        if pos > 8:
            break

if __name__ == '__main__':
    main()
