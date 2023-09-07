
############
Introduction
############


.. image:: https://readthedocs.org/projects/pymzml/badge/?version=latest
    :target: http://pymzml.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/pymzML.svg
   :target: https://pypi.org/project/pymzML/

.. image:: https://pepy.tech/badge/pymzml
   :target: https://pepy.tech/project/pymzml

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: As long it is black

.. image:: http://depsy.org/api/package/pypi/pymzML/badge.svg
  :target: http://depsy.org/package/python/pymzML
  :alt: Research software impact


*******************
General information
*******************

Module to parse mzML data in Python based on cElementTree

Copyright 2010-2021 by:

    | M. Kösters,
    | J. Leufken,
    | T. Bald,
    | A. Niehues,
    | S. Schulze,
    | K. Sugimoto,
    | R.P. Zahedi,
    | M. Hippler,
    | S.A. Leidel,
    | C. Fufezan,



===================
Contact information
===================

Please refer to:

    | Dr. Christian Fufezan
    | Group Leader Experimental Bioinformatics
    | Cellzome GmbH
    | R&D Platform Technology & Science
    | GSK
    | Germany
    | eMail: christian@fufezan.net
    |
    | https://fufezan.net


*******
Summary
*******

pymzML is an extension to Python that offers
    * a) easy access to mass spectrometry (MS) data that allows the rapid development of tools
    * b) a very fast parser for mzML data, the standard mass spectrometry data format
    * c) a set of functions to compare and/or handle spectra
    * d) random access in compressed files
    * e) interactive data visualization

**************
Implementation
**************

pymzML requires Python3.7+.
The module is freely available on pymzml.github.com or pypi,
published under MIT license and only requires numpy and regex, however there are several optional dependencies for extended functionality like interactive plotting and deconvolution.


********
Download
********

Get the latest version via github
    | https://github.com/pymzml/pymzML

The complete Documentation can be found as pdf
    | https://pymzml.readthedocs.io/_/downloads/en/latest/pdf/


********
Citation
********

M Kösters, J Leufken, S Schulze, K Sugimoto, J Klein, R P Zahedi, M Hippler, S A Leidel, C Fufezan; pymzML v2.0: introducing a highly compressed and seekable gzip format, Bioinformatics,
doi: https://doi.org/10.1093/bioinformatics/bty046


************
Installation
************

pymzML requires `Python`_ 3.7 or higher.

.. note::

    Consider to use a Python virtual environment for easy installation and use.
    Further, usage of python3.7+ is recommended.


Download pymzML using `GitHub`_ **or** the zip file:

* GitHub version: Start by cloning the GitHub repository::

   user@localhost:~$ git clone https://github.com/pymzML/pymzml.git
   user@localhost:~$ cd pymzml
   user@localhost:~$ pip install -r requirements.txt
   user@localhost:~$ python setup.py install

.. _Python:
   https://www.python.org/downloads/

.. _GitHub:
   https://github.com/pymzML/pymzml

* pypi version::

   user@localhost:~$ pip install pymzml # install standard version
   user@localhost:~$ pip install "pymzml[plot]" # with plotting support
   user@localhost:~$ pip install "pymzml[pynumpress]" # with pynumpress support
   user@localhost:~$ pip install "pymzml[deconvolution]" # with deconvolution support using ms_deisotope
   user@localhost:~$ pip install "pymzml[full]" # full featured


If you have troubles installing the dependencies, install numpy first separately,
since pynumpress requires numpy to be installed.

If you use Windows 7 please use the 'SDK7.1 command prompt' for installation
of pymzML to assure correct compiling of the C extensions.

=======
Testing
=======

To test the package and correct installation::

    tox


*************
Contributing
*************

Please read the contribution guidelines before contributing `here </CONTRIBUTING.rst>`_


****************
Code of Conduct
****************

Since pymzML is an open source project maintained by the community, we established a code of conduct
in order to facilitate an inclusive environment for all users, contributors and project memebers.
Before contributing to pymzML, please read the code of conduct `here </CODE_OF_CONDUCT.md>`_
