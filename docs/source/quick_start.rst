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



