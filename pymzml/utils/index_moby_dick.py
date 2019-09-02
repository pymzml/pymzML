"""
Example of how to use the :py:class:`~pymzml.utils.GSGW.GSGW` class to create
igzip file to load and create a copy of "Moby Dick" with every chapter indexed
with its number.
The file created can be read by :py:module:`~pymzml.utils.read_moby_dick`
"""

# Python mzML module - pymzml
# Copyright (C) 2010-2019 M. Kösters, C. Fufezan
#     The MIT License (MIT)

#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:

#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.

#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#     AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#     OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.

import urllib.request
import re
from GSGW import GSGW
import pymzml.regex_patterns as regex_patterns

moby_dick_url = (
    "http://faculty.washington.edu/stepp/courses/"
    "2004autumn/tcss143/lectures/files/2004-11-08/mobydick.txt"
)

response = urllib.request.urlopen(moby_dick_url)
moby_dick_txt = response.read().decode("utf-8").split("\n")


def index_by_chapter(txt):
    """
    Iterate the text file while collecting the data for each chapter and compressing it

    Args:
        txt(str): Moby Dick text as string
    """
    chapter_start = regex_patterns.MOBY_DICK_CHAPTER_PATTERN
    general_seekable_gzip_writer = GSGW(
        file="Moby_Dick_indexed.gz",
        max_idx=42,
        max_idx_len=9,
        max_offset_len=6,
        output_path="./Moby_Dick_indexed.gz",
    )

    with general_seekable_gzip_writer as index_writer:
        current_chapter = ""
        for line in txt:
            if re.match(chapter_start, line):
                match = re.match(chapter_start, line)
                current_chapter_number = int(match.group(1)) - 1
                print("indexing chapter {0}".format(current_chapter_number), end="\r")
                index = "Chapter{0}".format(current_chapter_number)
                index_writer.add_data(current_chapter, index)
                current_chapter = ""
            else:
                current_chapter += line
        current_chapter_number += 1

        index = "Chapter{0}".format(current_chapter_number)
        index_writer.add_data(current_chapter, index)
        print("index chapter {0} ".format(index), end="\r")
        index_writer.write_index()
        print("Indexed {0} chapters".format(current_chapter_number))


if __name__ == "__main__":
    index_by_chapter(moby_dick_txt)
