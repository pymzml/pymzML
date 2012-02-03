INTRODUCTION

Python module to interface mzML data in Python based on cElementTree
with additional tools for MS-informatics.

Copyright 2010-2011 by
                        T. Bald,
                        J. Barth,
                        A. Niehues,
                        M. Specht,
                        M. Hippler,
                        C. Fufezan


Mass spectrometry has evolved to a very diverse field that relies heavily on high throughput bioinformatics tools. Lately the consortium of mass spectrometry has published the first version of the mzML standard into which all mass spectrometry data should be able to be converted. This finally offers a unified representation of all mass spectrometric data. In order to rapidly develop bioinformatic tools that can explore the tremendous amount of data one needs a portable, robust, yet quick and easy interface to mzML files. The Python scripting language is predestined for such a task. pymzML is an object oriented Python module that adds the mzML interface to the Python interpreter. Although other interfaces exist in C/C++, none has the combination of a) the features of a scripting language, i.e. rapid development, easily readable source code applicable to all platforms and multiprocessing done with ease and b) the required speed of xml parsing for large data files. This makes pymzML and Python the optimal tools to rapidly develop bioinformatic tools for high throughput mass spectrometry.pymzML is hosted on github and freely available under LGPL, requires python2.6.5 or higher and is fully compatible with python 3


CITATION

Please cite us when using pymzml for your publications.
Bald, T., Barth, J., Niehues, A., Specht, M., Hippler, M., & Fufezan, C. (2012). pymzML - Python module for high throughput bioinformatics on mass spectrometry data. Bioinformatics, 1-2.
doi: 10.1093/bioinformatics/bts066


INSTALLATION

python setup.py install

(you might need admin privileges to write in the python site-package folder)


PARTICIPATE

If you like to participate, simply checkout the source code from our git hub at
http://github.com/pymzml, include in your changes and submit them to us.


DOCUMENTATION

For more in depth documentation of the modules and examples, please refer to
the documentation folder or http://github.com/pymzml


