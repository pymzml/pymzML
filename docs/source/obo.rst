.. obo:

.. default-domain:: py

##########
OBO parser
##########

.. automodule:: pymzml.obo


******************************
Accessing specific OBO MS tags
******************************

This section describes how to access some common MS tags by their names as they
are defined in the OBO file.

First pymzML is imported and the run is defined.

    >>> example_file = get_example_file.open_example('dta_example.mzML')
    >>> import pymzml
    >>> msrun = pymzml.run.Reader(example_file)

Now, we can fetch specific imformations from the spectrum object.

MS level:

    >>> for spectrum in msrun:
    ...     print(spectrum['ms level'])

Total Ion current:

    >>> for spectrum in msrun:
    ...     print(spectrum['total ion current'])


Furthermore we can also check for presence of parameters, therefore the
proprties of the spectrum.

Differentiation of e.g. HCD and CID fractionation:

    >>> for spectrum in msrun:
    ...     if spctrum['ms level'] == 2:
    ...         if 'collision-induced dissociation' in spectrum.keys():
    ...             print('Spectrum {0} is a CID spectrum'.format(spectrum['id']))
    ...         elif 'high-energy collision-induced dissociation' in spectrum.keys():
    ...             print('Spectrum {0} is a HCD spectrum'.format(spectrum['id']))


