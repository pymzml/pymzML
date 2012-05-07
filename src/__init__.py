# -*- pymzML -*-
# encoding: utf-8
# Copyright (c) 2009 <The authors in here!>
# module is distributed under the terms of the GNU General Public License
# See LICENSE for more details.

"""
Python mzML module - pymzml

Copyright (C) 2010-2011 T. Bald, J. Barth, M. Specht, M. Hippler, C. Fufezan 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = ['run', 'spec', 'obo', 'minimum', 'plot']

# Ensure the user is running the version of python we require.
import sys

if not hasattr(sys, "version_info") or sys.version_info < (2,6):
    raise RuntimeError("pymzml requires Python 2.6 or later.")
del sys

# Imports
from pymzml import *
