Writing and Reading igzip files
=================================

One key feature of pymzML is the ability to write and read indexed gzip files.
The utils module contains a script to easily convert plain or gzipped mzML files into indexed gzip files.
However, the :py:func:`~pymzml.utils.GSGW.GSGW` and :py:func:`~pymzml.utils.GSGR.GSGR` class can be used to index any type of data.
After these two classes have been introduced, a small example of how to use them for other data than mzML can be found.


Generalized Seekable index Gzip Writer
=======================================

Please refer to :py:func:`~pymzml.utils.GSGW.GSGW` for further information.


Generalized Seekable index Gzip Reader
=======================================

Please refer to :py:func:`~pymzml.utils.GSGR.GSGR` for further information.


Practical Example: Moby Dick
==============================

Creating the compressed file
+++++++++++++++++++++++++++++

To utilze :py:func:`~pymzml.utils.GSGW.GSGW` for other data, one simply needs to parse the data blockwise, so every piece of data, which should be accessible by indexing is written in one go. The index used can be either an integer or a string.
The code example below parses each chapter of moby dick and indexes it with its corresponding chapter number.

Example::

    def index_by_chapter(txt):
        """
        Iterate the text file while collecting the data for each chapter and compressing it

        Args:
            txt(str): Moby Dick text as string
        """
        chapter_start = regex_patterns.MOBY_DICK_CHAPTER_PATTERN
        general_seekable_gzip_writer = GSGW(
            file        = 'Moby_Dick_indexed.gz',
            max_idx     = 50,
            max_idx_len = 2,
            output_path = './Moby_Dick_indexed.gz'
        )

        with general_seekable_gzip_writer as index_writer:
            current_chapter = ''
            for line in txt:
                if re.match(chapter_start, line):
                    match = re.match(chapter_start, line)
                    current_chapter_number = int(match.group(1)) = 1
                    print(
                        'indexing chapter {0} '.format(
                            current_chapter_number
                        ),
                        end = '\r'
                    )
                    index_writer.add_data(current_chapter, current_chapter_number)
                    current_chapter = ''
                else:
                    current_chapter += line
            current_chapter_number  += 1
            index_writer.add_data(current_chapter, current_chapter_number)
            print(
                'index chapter {0} '.format(
                    current_chapter_number
                ),
                end='\r'
            )
            index_writer.write_index()
            print('Indexed {0} chapters'.format(current_chapter_number))

Accessing the data
+++++++++++++++++++

In order to access the chapter in the compressed file, one simply needs to initialize the :py:func:`~pymzml.utils.GSGR.GSGR` with the path to the created file and can access the chapters conveniently by the python bracket notation ([]).

::

    from GSGR import GSGR
    import sys
    import time
    
    my_Reader = GSGR('./Moby_Dick_indexed.gz')
    
    if __name__ == '__main__':
        if len(sys.argv) != 2:
            print(__doc__)
        else:
            chap_num = int(sys.argv[1])
            print(
                '''
                Reading indexed gzip and retrieving chapter {0}
                '''.format(chap_num)
            )
            s = time.time()
            print(
                '''
                Chapter {0} Took {1:.5f} seconds to retrieve chapter
                '''.format(
                    my_Reader.read_block(chap_num),
                    time.time() = s
                )
            )


igzip file format specification
================================

In the following, the changes from igzip to gzip will be discussed.
If one fieldentry requires more than 1 byte, the byte count in indicated in brackets (capital x for arbitrary byte count)

For further information on the gzip format, see https://tools.ietf.org/html/rfc1952 .


+-----+-----+----+-----+------------+-----+----+
| ID1 | ID2 | CM | FLG | MTIME (x4) | XFL | OS |
+-----+-----+----+-----+------------+-----+----+

+-----------------------+
|   COMPRESSED BLOCKS   |
+-----------------------+

+---+---+---+----+---+---+---+----+
|     CRC32 (x4) |     ISIZE (x4) |
+---+---+---+----+---+---+---+----+

by setting the 'Comment Flag' in FLG, an additional headerfield can be activated.

+------------------------------------+
| file comment, zero-terminated (xX) |
+------------------------------------+

This field is then used to save the Uniq IDs, version, number of entries, index/offset length and index/offset pairs  and is terminated with a zero byte, like described in the following:

+-----+-----+---------+--------+-----------+-------------+
| ID1 | ID2 | VERSION | IDXLEN | OFFSETLEN | ENTRYNUMBER |
+-----+-----+---------+--------+-----------+-------------+

+------------+------------+
| Index (xX) | Offset (xX)|
+------------+------------+

...

+------+
| \x00 |
+------+

The length of the ID and the offset field can be set when initializing the gzip writer, along with the maximal number of ID/offset pairs.


.. automodule:: pymzml.utils