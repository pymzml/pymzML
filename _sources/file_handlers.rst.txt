File Access
===========

pymzML offers support for different kinds of mzML files.
The following classes are wrappers for access of different types of mzML
files, which allows the implementation of file type specific search and data retrieving algorithms.
An explanation of how to implement your own file class can be found in the advanced usage section.

File Interface
--------------

.. autoclass:: pymzml.file_interface.FileInterface
	:members:
	:exclude-members: __weakref__, close, __del__
	:private-members:
	:special-members:

File Classes
------------

mzML
++++

.. autoclass:: pymzml.file_classes.standardMzml.StandardMzml
    :members:
    :exclude-members: _read_to_spec_end, _read_until_tag_end, close, __weakref__, __del__
    :private-members:
    :special-members:


Gzip
++++

.. autoclass:: pymzml.file_classes.standardGzip.StandardGzip
    :members:
    :exclude-members: __weakref__, __del__
    :private-members:
    :special-members:


iGzip
+++++

.. autoclass:: pymzml.file_classes.indexedGzip.IndexedGzip
    :members:
    :exclude-members: close, __weakref__, __del__
    :private-members:
    :special-members:

