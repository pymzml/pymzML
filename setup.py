#!/usr/bin/env python3
from setuptools import setup
import os

version_path = os.path.join(
    os.path.dirname(__file__),
    'pymzml',
    'version.txt'
)
with open(version_path, 'r') as version_file:
    pymzml_version = version_file.read().strip()

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
    python_requires  = '>=3.7.0',
    install_requires = [
        'numpy >= 1.8.0',
        'regex',
    ],
    extras_require   = {
        'full': [
            'plotly<5.6',
            'pynumpress>=0.0.4',
            'ms_deisotope',
        ],
        'plot': ['plotly<5.6'],
        'pynumpress': ['pynumpress>=0.0.4'],
        'deconvolution': ['ms_deisotope==0.0.14'] 
    },
    description      = 'high-throughput mzML parsing',
    long_description = 'pymzML - python module for mzML parsing',
    author           = 'M. Koesters, J. Leufken, S. Schulze, K. Sugimoto, R. Zahedi, M. Hippler and C. Fufezan',
    author_email     = 'christian@fufezan.net',
    url              = 'http://pymzml.github.com',
    license          = 'The MIT license',
    platforms        = 'any that supports python 3.7',
    classifiers      = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ]
)
