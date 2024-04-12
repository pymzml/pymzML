.. pymzml_utils:

Utils
=====

.. General
.. ----------

.. These are the different APIS for supported file formats
.. Currently: mzML, mzML.gz, mzML.igzip


GSGW
----

.. autoclass:: pymzml.utils.GSGW.GSGW
	:members:
	:private-members:
	:exclude-members: __del__, __enter__, __exit__, close


GSGR
----

.. autoclass:: pymzml.utils.GSGR.GSGR
	:members:
	:private-members:
	:exclude-members: __enter__, __exit__, _read_until_zero, close


.. Creating a custom Filehandler
.. ------------------------------

.. Introduction
.. +++++++++++++

.. It is also possible to create an own API for different forms
.. of mzML files. For this, a new class needs to be written, which
.. implements a `read` and a `__getitem__` function.


.. Implementation of the API Class
.. ++++++++++++++++++++++++++++++++

Example::

.. 	class SQLiteDatabase(object):
.. 		"""
.. 		Example implementation of a database Connector,
.. 		which can be used to make run accept paths to
.. 		sqlite db files.

.. 		We initialize with a path to a database and implement
.. 		a custom __getitem__ function to retrieve the spectra
.. 		"""

.. 		def __init__(self, path):
.. 			"""
.. 			"""
.. 			connection = sqlite3.connect(path)
.. 			self.cursor = connection.cursor()

.. 		def __getitem__(self, key):
.. 			"""
.. 			Execute a SQL request, process the data and return a spectrum object.

.. 			Args:
.. 				key (str or int): unique identifier for the given spectrum in the
.. 				database
.. 			"""
.. 			self.cursor.execute('SELECT * FROM spectra WHERE id=?', key)
.. 			ID, element = self.cursor.fetchone()

.. 			element = et.XML(element)
.. 			if 'spectrum' in element.tag:
.. 				spectrum = spec.Spectrum(element)
.. 			elif 'chromatogram' in element.tag:
.. 				spectrum = spec.Chromatogram(element)
.. 			return spectrum

.. 		def get_spectrum_count(self):
.. 			self.cursor.execute("SELECT COUNT(*) from spectra")
.. 			num = self.cursor.fetchone()[0]
.. 			return num

.. 		def read(self, size=-1):
.. 			# implement read so it starts reading in first ID,
.. 			# if end reached switches to next id and so on ...

.. 			return '<spectrum index="0" id="controllerType=0 controllerNumber=1 scan=1" defaultArrayLength="917"></spectrum>\n'

.. Enabling the new API Class in File Interface
.. +++++++++++++++++++++++++++++++++++++++++++++

.. In order to make the run class accept the new file class, one need to edit
.. the :py:func:`_open` function in file_interface.py


Example::

.. 	def _open(self, path):
.. 		if path.endswith('.gz'):
.. 			if self._indexed_gzip(path):
.. 				self.file_handler = indexedGzip.IndexedGzip(path, self.encoding)
.. 			else:
.. 				self.file_handler = standardGzip.StandardGzip(path, self.encoding)
.. 		# Insert a new condition to enable your new fileclass
.. 		elif path.endswith('.db'):
.. 			self.file_handler = utils.SQLiteConnector.SQLiteDatabase(path, self.encoding)
.. 		else:
.. 			self.file_handler     = standardMzml.StandardMzml(path, self.encoding)
.. 		return self.file_handler


.. Moby Dick as indexed Gzip
.. ---------------------------

.. Example of how to use the GSGW and GSGR class to create and access indexed Gzip files
.. .. code-block:: bash


.. 	python3 index_moby_dick.py

.. 	python3 read_moby_dick.py 10



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
