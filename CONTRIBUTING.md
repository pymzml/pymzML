Contribution Guidelines
#######################

*pymzML - an interface between Python and mzML Mass spectrometry Files*

Summary
*******

In general, contribution to pymzML is very welcome! Feel free to fork and/or clone
pymzML. If you want to improve code or contribute new features/tools/algorithms
please read these guidelines first. If something is unclear please contact one
of the authors for help or let us know via e.g. an issue.

We are happy to include your name to the list of contributors in the `README`_.
Drop a line to one of the developers if you want to get included (and of course
you actually contributed something)

.. _README:
   https://github.com/pymzml/pymzML/blob/master/README.rst

Commit messages
***************

First of all, please be concise and as descriptive (explicit is better than
implicit :) ) as possible. It is always
helpful to point out, which parts of pymzML were changed/fixed (e.g.
documentation or example scripts etc. ). In the same time, please avoid
unneccesarily long messages.
If possible, always use a headline in your commit message and list all changes as bullet points.


Code standards and conventions
******************************

Since this a collaborative project, you will encounter different coding styles.
Despite the fact that we know that diversity is beautiful, we need to keep some
common line on how to code (This list may be further extended). We generally use
PEP8 style (https://www.python.org/dev/peps/pep-0008/) with the exception of
E203 (whitespaces before : in order to align values in dicts). Additionally 
this list will give you some things to think about:

  | Re-think naming of variables at least twice
  | Re-check deleting of own debug code before sending Pull requests
  | Re-check own files created by nosetests and add it into '.gitignore' before sending Pull requests
  
---
**NOTE**

In future we might change to using black (https://github.com/python/black) to have one clear standard for code formatting.

---


Test philosophy
***************

Test your code! Seriously, test you code! If you add new functionality or nodes
at the same time provide (a) test function(s). We have already a set of tests
and different files, which can be used for the test. Avoid adding new test files
if possible to keep the repo small.


Sphinx guide
************

We use Sphinx to automatically build and format the documentation. Please keep
this style in your docstrings


Other rules and cosiderations
*****************************

None so far.

Merge/pull requests
*******************

Please use the pull request to push your code to the master repository. It will
be automatically tested by Travis and AppVeyor if the module is still working in
unix and Windows environments. Pull requests will be discussed by the main dev
team and merged into pymzML.


Issues
******

If you have an issue or problem, please first search all open issues and pull
request to avoid duplication of efforts. If you have a fix for the problem you
may directly open a pull requets. On the other hand, if you plan to or
are already working on implementing new stuff, you may also open an issue and
(pre-) announce your contribution. Please tag then the issue with
'enhancement'. In general the core team of pymzML will also take care of crucial
bugs in the main code. Since pymzML is open source, we cannot maintain every detail
and assure its compatibility and functionality (please be reminded here to test
your code, seriously, test your code)


Citation
********

Be reminded, that in an academic world, citations are the only credit that one can hope for ;)
If you use pymzML, do not forget to cite us

*M Kösters, J Leufken, S Schulze, K Sugimoto, J Klein, R P Zahedi, M Hippler, S A Leidel, C Fufezan; pymzML v2.0: introducing a highly compressed and seekable gzip format, Bioinformatics, doi: https://doi.org/10.1093/bioinformatics/bty046*

.. _publicationtitle: https://doi.org/10.1093/bioinformatics/bty046
.. |publicationtitle| replace:: *pymzML v2.0: introducing a highly compressed and seekable gzip format*
