.. _example_scripts:

Example Scripts
================

Parsing a mzML file (new syntax)
--------------------------------

.. autofunction:: simple_parser.main

.. include:: code_inc/simple_parser.inc


Parsing a mzML file (old syntax)
--------------------------------

.. autofunction:: simple_parser_v2.main

.. include:: code_inc/simple_parser_v2.inc


Query the obo files
-------------------

.. autofunction:: queryOBO.main

.. include:: code_inc/queryOBO.inc


Plotting a chromatogram
-----------------------

.. autofunction:: plot_chromatogram.main

.. include:: code_inc/plot_chromatogram.inc


Plotting a spectrum
-------------------

.. autofunction:: plot_spectrum.main

.. include:: code_inc/plot_spectrum.inc


Plotting a spectrum with annotation
-----------------------------------

.. autofunction:: plot_spectrum_with_annotation.main

.. include:: code_inc/plot_spectrum_with_annotation.inc



Extracting highest peaks
------------------------

.. autofunction:: highest_peaks.main

.. include:: code_inc/highest_peaks.inc


Compare spectra
---------------

.. autofunction:: compare_spectra.main

.. include:: code_inc/compare_spectra.inc


Find m/z values
---------------

.. autofunction:: has_peak.main

.. include:: code_inc/has_peak.inc


Extract ion chromatogram
------------------------

.. autofunction:: extract_ion_chromatogram.main

.. include:: code_inc/extract_ion_chromatogram.inc


Find abundant precursors
------------------------

.. autofunction:: get_precursors.main

.. include:: code_inc/get_precursors.inc


Access polarity of spectra
--------------------------

.. autofunction:: polarity.main

.. include:: code_inc/polarity.inc


Check old to new function name mapping
--------------------------------------

.. autofunction:: deprecation_check.main

.. include:: code_inc/deprecation_check.inc


Convert mzML(.gz) to mzML.gz (igzip)
------------------------------------

.. autofunction:: gzip_mzml.main

.. include:: code_inc/gzip_mzml.inc


Creating a custom Filehandler
------------------------------

Introduction
+++++++++++++

It is also possible to create an own API for different forms
of mzML files. For this, a new class needs to be written, which
implements a `read` and a `__getitem__` function.


Implementation of the API Class
++++++++++++++++++++++++++++++++

Example::

	class SQLiteDatabase(object):
		"""
		Example implementation of a database Conncetor,
		which can be used to make run accept paths to
		sqlite db files.

		We initialize with a path to a database and implement
		a custom __getitem__ function to retrieve the spectra
		"""

		def __init__(self, path):
			"""
			"""
			connection = sqlite3.connect(path)
			self.cursor = connection.cursor()

		def __getitem__(self, key):
			"""
			Execute a SQL request, process the data and return a spectrum object.

			Args:
				key (str or int): unique identifier for the given spectrum in the
				database
			"""
			self.cursor.execute('SELECT * FROM spectra WHERE id=?', key)
			ID, element = self.cursor.fetchone()

			element = et.XML(element)
			if 'spectrum' in element.tag:
				spectrum = spec.Spectrum(element)
			elif 'chromatogram' in element.tag:
				spectrum = spec.Chromatogram(element)
			return spectrum

		def get_spectrum_count(self):
			self.cursor.execute("SELECT COUNT(*) from spectra")
			num = self.cursor.fetchone()[0]
			return num

		def read(self, size=-1):
			# implement read so it starts reading in first ID,
			# if end reached switches to next id and so on ...
		
			return '<spectrum index="0" id="controllerType=0 controllerNumber=1 scan=1" defaultArrayLength="917"></spectrum>\n'	

Enabling the new API Class in File Interface
+++++++++++++++++++++++++++++++++++++++++++++

In order to make the run class accept the new file class, one need to edit
the :py:func:`_open` function in file_interface.py

Example::

	def _open(self, path):
		if path.endswith('.gz'):
			if self._indexed_gzip(path):
				self.file_handler = indexedGzip.IndexedGzip(path, self.encoding)
			else:
				self.file_handler = standardGzip.StandardGzip(path, self.encoding)
		# Insert a new condition to enable your new fileclass
		elif path.endswith('.db'):
			self.file_handler = utils.SQLiteConnector.SQLiteDatabase(path, self.encoding)
		else:
			self.file_handler     = standardMzml.StandardMzml(path, self.encoding)
		return self.file_handler


Moby Dick as indexed Gzip
---------------------------

Example of how to use the GSGW and GSGR class to create and access indexed Gzip files
	
.. code-block:: bash


	python3 index_moby_dick.py

	python3 read_moby_dick.py 10
		


.. Scripts
.. --------

.. pymzML ships with some usefull scripts, which are described in the following

.. Create indexed gziped conveniently
.. +++++++++++++++++++++++++++++++++++

.. blub

.. Find optimal read size
.. +++++++++++++++++++++++

.. Hard drives have different sector sizes, ....

.. utils -- A collection of useful functions
.. ++++++++++++++++++++++++++++++++++++++++++

.. blub
