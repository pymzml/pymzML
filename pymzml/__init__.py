# -*- pymzML -*-
# encoding: utf-8

"""
Python mzML module - pymzml
Copyright (C) 2010-2016 M. Kösters, C. Fufezan
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
__all__ = ["run", "spec", "obo", "minimum", "plot", "file_classes"]

import os
import sys

if not hasattr(sys, "version_info") or sys.version_info < (3, 4):
    raise RuntimeError("pymzML requires Python 3.4 or later.")

# Set version
version_path = os.path.join(os.path.dirname(__file__), "version.txt")
with open(version_path, "r") as version_file:
    __version__ = version_file.read().strip()

# Imports of individual modules
import pymzml.run
import pymzml.spec
from pymzml.spec import MSDecoder
import pymzml.obo
import pymzml.plot
import pymzml.utils
