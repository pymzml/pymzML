#!/usr/bin/env python3
# encoding: utf-8

'''

Originally created for Ursgal ( https://github.com/ursgal/ursgal )


'''

import glob
import os

if __name__ == '__main__':
    print('''
        Formatting example scripts into rst files for the docs
''')
    # input()
    example_script_path = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'example_scripts',
        '*.py',
    )
    print(example_script_path)
    for example_script in glob.glob(example_script_path):
        if os.path.exists(example_script) is False:
            continue
        basename = os.path.basename(example_script)
        print(
            'Reading: {0}'.format(example_script)
        )
        file_path = os.path.join(
            os.path.dirname(__file__),
            'source',
            'code_inc',
            '{0}',
        )
        with open( file_path.format( basename.replace('.py', '.inc')), 'w') as o:
            print('''.. code-block:: python\n''', file=o)
            with open( example_script ) as infile:
                for line in infile:
                    print('\t{0}'.format( line.rstrip()), file=o)


