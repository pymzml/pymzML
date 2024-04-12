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

This field is then used to save the Uniq IDs, version, index/offset length and is terminated with a zero byte, like described in the following:

+-----+-----+---------+--------+-----------+
| ID1 | ID2 | VERSION | IDXLEN | OFFSETLEN |
+-----+-----+---------+--------+-----------+

+------------+------------+
| Index (xX) | Offset (xX)|
+------------+------------+

...

+------+
| \x00 |
+------+

The length of the ID and the offset field can be set when initializing the gzip writer, along with the maximal number of ID/offset pairs.

Example::

    00000000:  1f8b 0810 ea57 4f5a 0203 4655 0109 06ac 4368 6170 7465 7230  :.....WOZ..FU....Chapter0
    00000018:  acac ac36 3436 ac43 6861 7074 6572 31ac 3136 3033 32ac 4368  :...646.Chapter1.16032.Ch
    00000030:  6170 7465 7232 ac32 3137 3831 ac43 6861 7074 6572 33ac 3235  :apter2.21781.Chapter3.25
    00000048:  3534 37ac 4368 6170 7465 7234 ac33 3932 3436 ac43 6861 7074  :547.Chapter4.39246.Chapt
    00000060:  6572 35ac 3433 3435 38ac 4368 6170 7465 7236 ac34 3535 3437  :er5.43458.Chapter6.45547
    00000078:  ac43 6861 7074 6572 37ac 3437 3936 39ac 4368 6170 7465 7238  :.Chapter7.47969.Chapter8
    00000090:  ac35 3037 3033 ac43 6861 7074 6572 39ac 3533 3239 3943 6861  :.50703.Chapter9.53299Cha
    000000a8:  7074 6572 3130 ac36 3230 3138 4368 6170 7465 7231 31ac 3636  :pter10.62018Chapter11.66
    000000c0:  3032 3843 6861 7074 6572 3132 ac36 3739 3536 4368 6170 7465  :028Chapter12.67956Chapte
    000000d8:  7231 33ac 3730 3333 3043 6861 7074 6572 3134 ac37 3438 3331  :r13.70330Chapter14.74831
    000000f0:  4368 6170 7465 7231 35ac 3736 3938 3443 6861 7074 6572 3136  :Chapter15.76984Chapter16
    00000108:  ac38 3030 3937 4368 6170 7465 7231 37ac 3933 3134 3743 6861  :.80097Chapter17.93147Cha
    00000120:  7074 6572 3138 ac39 3838 3534 4368 6170 7465 7231 3931 3032  :pter18.98854Chapter19102
    00000138:  3430 3343 6861 7074 6572 3230 3130 3533 3932 4368 6170 7465  :403Chapter20105392Chapte
    00000150:  7232 3131 3037 3739 3043 6861 7074 6572 3232 3131 3037 3232  :r21107790Chapter22110722
    00000168:  4368 6170 7465 7232 3331 3134 3936 3143 6861 7074 6572 3234  :Chapter23114961Chapter24
    00000180:  3131 3631 3134 4368 6170 7465 7232 3531 3230 3731 3943 6861  :116114Chapter25120719Cha
    00000198:  7074 6572 3236 3132 3135 3633 4368 6170 7465 7232 3731 3234  :pter26121563Chapter27124
    000001b0:  3839 3343 6861 7074 6572 3238 3132 3933 3138 4368 6170 7465  :893Chapter28129318Chapte
    000001c8:  7232 3931 3333 3134 3843 6861 7074 6572 3330 3133 3633 3436  :r29133148Chapter30136346
    000001e0:  4368 6170 7465 7233 3131 3337 3230 3043 6861 7074 6572 3332  :Chapter31137200Chapter32
    000001f8:  3133 3933 3137 4368 6170 7465 7233 3331 3532 3031 3743 6861  :139317Chapter33152017Cha
    00000210:  7074 6572 3334 3135 3437 3635 4368 6170 7465 7233 3531 3630  :pter34154765Chapter35160
    00000228:  3536 3743 6861 7074 6572 3336 3136 3732 3736 4368 6170 7465  :567Chapter36167276Chapte
    00000240:  7233 3731 3734 3530 3243 6861 7074 6572 3338 3137 3630 3330  :r37174502Chapter38176030
    00000258:  4368 6170 7465 7233 3931 3737 3230 3043 6861 7074 6572 3430  :Chapter39177200Chapter40
    00000270:  3137 3830 3338 4368 6170 7465 7234 3131 3832 3531 3900

In this example of the Moby Dick igz header, the first 10 bytes show the gzip header explained above.
After the first 10 bytes, the comment field starts with the 2 ID bytes F and U and version 1.
The Idx len is set to have a length of 9 and the offset needs to fit in 6 bytes.
After this, the index to offset mapping starts until the zero byte is reached.
