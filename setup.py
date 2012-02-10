#!/usr/bin/env python3

from distutils.core import setup
setup(name='pymzml',
      version='0.7.4',
      packages = ['pymzml'],
      package_dir = {'pymzml': 'src'},
      package_data={'pymzml': ['obo/*.obo']},
      description='high-throughput mzML parsing',
      long_description='pymzML - python module for mzML parsing',
      author='T. Bald, J. Barth, A. Niehues, M. Specht, M. Hippler, C. Fufezan',
      author_email='christian@fufezan.net',
      url='http://pymzml.guthub.com',
      license='Lesser GNU General Public License (LGPL)',
      platforms='any that supports python 2.6.5',
      classifiers=[
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
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 2.2',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Medical Science Apps.',
            'Topic :: Scientific/Engineering :: Education',
            'Topic :: Software Development :: Libraries :: Python Modules'
            ],
      )


