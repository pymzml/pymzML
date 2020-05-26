.. _quick-start:

Quick Start
===========

Parsing a mzML file and setting measured precision
--------------------------------------------------


.. autofunction:: simple_parser.main
	:noindex:

.. include:: code_inc/simple_parser.inc


Seeking in a mzML file
----------------------

One of the features of pymzML is the ability to (create) and read
indexed gzip which allows mzML file sizes to reach the levels of the original
RAW format. The interface to random access into a mzML file is implemented
by the magic get function in pymzMLs run class.

Alternatively, pymzML can also rapidly seek into any uncompressed mzML file,
no matter if an index was included into the file or not.

.. code-block:: python

    #!/usr/bin/env python
    import pymzml

    run = pymzml.run.Reader( 'tests/data/BSA1.mzML.gz' )
    spectrum_with_id_2540 = run[ 2540 ]


Reading mzML indices with a custom regular expression
------------------------------------------------------

When reading mzML files with indices wich is not an integer or contains "scan=1" or similar,
you can set a custom regex to parse the index when initializing the reader.

Say for example you have an index as in the example file Manuels_customs_ids.mzML:
    <offset idRef="ManuelsCustomID=1 diesdas">4026</offset>

.. code-block:: python

    #!/usr/bin/env python
    import pymzml
    import re

    index_re = re.compile(
        b'.*idRef="ManuelsCustomID=(?P<ID>.*) diesdas">(?P<offset>[0-9]*)</offset>'
    )
    run = pymzml.run.Reader(your_file_path, index_regex=index_re)
    spec_1 = run[1]

The regular expression has to contain a group called ID and a group called offset.
Also be aware that your regex need to be a byte string.

