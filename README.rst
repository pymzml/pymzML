
############
Introduction
############

The latest Documentation was generated on: |today|


*******************
General information
*******************

Module to parse mzML data in Python based on cElementTree

Copyright 2010-2017 by:

    | M. Kösters,
    | J. Leufken,
    | Bald, Till
    | Niehues, Anna
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
    | Institute of Plant Biology and Biotechnology
    | Schlossplatz 8 , R 105
    | University of Muenster
    | Germany
    | eMail: christian@fufezan.net
    | Tel: +049 251 83 24861
    |
    | http://www.uni-muenster.de/Biologie.IBBP.AGFufezan


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

pymzML requires Python3.4+.
The module is freely available on pymzml.github.com or pypi,
published under GPL and requires no additional modules to be installed, but can 
optionally use numpy.


********
Download
********

Get the latest version via github
    | https://github.com/pymzml/pymzML

or the latest package at
    | http://pymzml.github.com/dist/pymzml.tar.bz2
    | http://pymzml.github.com/dist/pymzml.zip

The complete Documentation can be found as pdf
    | http://pymzml.github.com/dist/pymzml.pdf


********
Citation
********

To be anounced


************
Installation
************

pymzML requires `Python`_ 3.4 or higher.

.. note::

    Consider to use a Python virtual environment for easy installation and use. 
    Further, usage of python3.4+ is recommended.


Download pzmzML using `GitHub`_ **or** the zip file:

* GitHub version: Start by cloning the GitHub repository::

   user@localhost:~$ git clone https://github.com/pymzML/pymzml.git
   user@localhost:~$ cd pymzml
   user@localhost:~$ pip install -r requirements.txt
   user@localhost:~$ python setup.py install

.. _Python:
   https://www.python.org/downloads/

.. _GitHub:
   https://github.com/pymzML/pymzml


If you use Windows 7 please use the 'SDK7.1 command prompt' for installation
of pymzML to assure correct compiling of the C extensions.



