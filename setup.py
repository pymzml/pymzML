#!/usr/bin/env python3
import os, requests, platform
from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
# from pymzml.version import pymzml_version
try:
    import numpy
except:
    numpy = None
from compile_tools import eof_changer, include_add

# numpress directory path
numpress_dir_path = os.path.join(
    os.path.dirname(__file__),
    'Numpress'
)
if os.path.isdir(numpress_dir_path) is not True:
    os.mkdir(numpress_dir_path)

# grab dat files
hpp = requests.get(
    'https://raw.githubusercontent.com/'
    'ms-numpress/ms-numpress/master/src/main/cpp/MSNumpress.hpp'
)
with open(
    os.path.join(
        numpress_dir_path,
        'MSNumpress.hpp'
    ),
    'w'
) as hpp_file:
    hpp_file.write(hpp.text)

cpp = requests.get(
    'https://raw.githubusercontent.com/'
    'ms-numpress/ms-numpress/master/src/main/cpp/MSNumpress.cpp'
)
with open(
    os.path.join(
        numpress_dir_path,
        'MSNumpress.cpp'
    ),
    'w'
) as cpp_file:
    cpp_file.write(cpp.text)

# Add algorithm
MSNumpress_path = os.path.join(
    numpress_dir_path,
    'MSNumpress.cpp'
)
insertions = ['#include <algorithm>']
include_add.add_insertions_into_files(
    [MSNumpress_path],
    insertions
)

# EOF replacement
eof_changer.EOF_change_in_dir(numpress_dir_path)

extra_compile_args = []
pltf = platform.system()
if pltf == 'Windows':
    extra_compile_args = ['/EHsc']

if numpy is not None:
    ext_modules = [
        Extension(
            "PyNumpress",
            [
                os.path.join(
                    numpress_dir_path,
                    'PyNumpress.pyx',
                ),
                os.path.join(
                    numpress_dir_path,
                    'MSNumpress.cpp',
                ),
            ],
            language           = 'c++',
            extra_compile_args = extra_compile_args,
        )
    ]
else:
    ext_modules = []


# We store our version number in a simple text file:
# version_path = os.path.join(
#     os.path.dirname(__file__),
#     'pymzml', 'version.txt'
# )
# with open(version_path, 'r') as version_file:
#     pymzml_version = version_file.read().strip()
from pymzml.version import pymzml_version

numpy_include_dirs = None
if numpy is not None:
    numpy_include_dirs = numpy.get_include()

setup(
    name             = 'pymzml',
    version          = pymzml_version,
    packages         = ['pymzml', 'pymzml.file_classes', 'pymzml.utils'],
    package_dir      = {'pymzml': 'pymzml'},
    package_data     = {
        'pymzml': [
            'version.txt',
            'obo/*.obo.gz'
        ]
    },
    # include_dirs     = [numpy.get_include() if numpy is not None else None for x in range(1)],
    # ^-- this has potential for https://thedailywtf.com/series/code-sod
    # Personal favorite: http://thedailywtf.com/articles/the-wrong-sacrifice
    # Thanks for tingling me with this!
    include_dirs     = [ numpy_include_dirs ],
    ext_modules      = ext_modules,
    cmdclass         = {'build_ext': build_ext},
    description      = 'high-throughput mzML parsing',
    long_description = 'pymzML - python module for mzML parsing',
    author           = 'M. Koesters, J. Leufken, S. Schulze, K. Sugimoto, R. Zahedi and C. Fufezan',
    author_email     = 'christian@fufezan.net',
    url              = 'http://pymzml.github.com',
    license          = 'GNU General Public License (GPL)',
    platforms        = 'any that supports python 3.4',
    classifiers      = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)


