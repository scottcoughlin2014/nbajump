#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) Giacomo Terreran (2021)
#
# This file is part of the jumpnba python package.
#
# jumpnba is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpnba is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpnba.  If not, see <http://www.gnu.org/licenses/>.

"""Setup the jumpnba package
"""

from __future__ import print_function

import glob
import os.path
import sys

from setuptools import (setup, find_packages)

cmdclass = {}

# -- versioning ---------------------------------------------------------------

import versioneer
__version__ = versioneer.get_version()
cmdclass.update(versioneer.get_cmdclass())

# -- documentation ------------------------------------------------------------

# import sphinx commands
try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    pass
else:
    cmdclass['build_sphinx'] = BuildDoc

# read description
with open('README.md', 'rb') as f:
    longdesc = f.read().decode().strip()

# -- dependencies -------------------------------------------------------------

if 'test' in sys.argv:
    setup_requires = [
        'setuptools',
        'pytest-runner',
    ]
else:
    setup_requires = []

# These pretty common requirement are commented out. Various syntax types
# are all used in the example below for specifying specific version of the
# packages that are compatbile with your software.
install_requires = [
    'requests',
    'django',
    #'pyblast @ https://github.com/CIERA-Northwestern/pyblast/tarball/master',
    #'scipy >= 0.12.1',
    #'matplotlib >= 1.2.0, != 2.1.0, != 2.1.1',
    #'astropy >= 1.1.1, < 3.0.0 ; python_version < \'3\'',
    #'astropy >= 1.1.1 ; python_version >= \'3\'',
    #'configparser',
    #'pandas >= 0.24',
]

tests_require = [
    "pytest >= 3.3.0",
    "pytest-cov >= 2.4.0",
]

# For documenation
extras_require = {
    'doc': [
        'matplotlib',
        'ipython',
        'sphinx',
        'numpydoc',
        'sphinx_rtd_theme',
        'sphinxcontrib_programoutput',
    ],
}

# -- run setup ----------------------------------------------------------------
packagenames = find_packages()

# Executables go in a folder called bin
scripts = glob.glob(os.path.join('bin', '*'))

PACKAGENAME = 'jumpnba'
DISTNAME = 'django-jumpnba' #'YOUR DISTRIBTUION NAME (I.E. PIP INSTALL DISTNAME)' Generally good to be same as packagename
AUTHOR = 'Giacomo Terreran'
AUTHOR_EMAIL = 'gqterre@gmail.com'
LICENSE = 'GPLv3+'
DESCRIPTION = 'A Django application to track proficiencies of NBA teams to score first written by Giacomo Terreran <gqterre@gmail.com>, Scott Coughlin <scottcoughlin2014@u.northwestern.edu>, and Kyle Kremer <kylekremer23@gmail.com>'
GITHUBURL = 'https://github.com/scottcoughlin2014/nbajump.git'

setup(name=DISTNAME,
      provides=[PACKAGENAME],
      version=__version__,
      description=DESCRIPTION,
      long_description=longdesc,
      long_description_content_type='text/markdown',
      #ext_modules = [wrapper], ONLY IF WRAPPING C C++ OR FORTRAN
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      packages=packagenames,
      include_package_data=True,
      cmdclass=cmdclass,
      url=GITHUBURL,
      scripts=scripts,
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=extras_require,
      python_requires='>3.5, <4',
      use_2to3=True,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Intended Audience :: Science/Research',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      ],
)
