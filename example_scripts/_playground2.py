#!/usr/bin/env python3
import bisect
import pprint
import click
import os
import hashlib

import random
import pickle
import pymzml

from xml.etree.ElementTree import ParseError


@click.command()
@click.argument('input_files', nargs=-1)
@click.option('--shuffle', '-s', is_flag=True)
@click.option('--suffix')
def main(input_files, shuffle, suffix=''):
    print(suffix)
    output_name = f'failing_spectra{suffix}.txt'
    with open(output_name, 'wt') as fout:
        for file in input_files:
            print(file)
            fails = 0
            fail_info = []
            reader = pymzml.run.Reader(file)
            indices = list(range(1, reader.get_spectrum_count()))
            if shuffle:
                random.seed(a=1570010244.2805517)
                random.shuffle(indices)
                m = hashlib.md5()
                m.update(pickle.dumps(indices))
                md5_digest = m.hexdigest()
                print(f"Shuffled indices md5: {md5_digest}")
                # exit(1)
            number_of_specs = len(indices)
            basic_off_set_dict = reader.info["file_object"].file_handler.offset_dict.copy()
            basic_seek_list = reader.info["file_object"].file_handler.seek_list.copy()
            for pos, i in enumerate(indices):
                # reader.info["file_object"].file_handler.offset_dict = basic_off_set_dict.copy()
                # reader.info["file_object"].file_handler.seek_list = basic_seek_list.copy()
                current_precentage = 100 * float(pos) / float(number_of_specs)
                print(f"[{current_precentage:0>3.1f}%] Access spectrum {i:<10}".format(), end='\r')
                #spec = reader[i]
                try:
                    spec = reader[i]
                    # 100 / 0
                except Exception as e:
                    fails += 1
                    fout.write(f'{os.path.basename(file)}\t{i}\n')
                    print(f"failed on spec {i}")

                    # pprint.pprint(reader.info["file_object"].file_handler.offset_dict)
                    # pprint.pprint(reader.info["file_object"].file_handler.seek_list)
                    spec = reader[i]
                    exit(1)
                # break
            print()
            perc = fails / len(indices) * 100
            print(f'{fails} of {len(indices)} spectra could not be accessed ({perc}%)')
            print('\n\n')


if __name__ == '__main__':
    main()
