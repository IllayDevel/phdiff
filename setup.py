#!/usr/bin/env python3

import re
from setuptools import setup
from setuptools import find_packages
from setuptools import Extension


def find_version():
    return re.search(r"^__version__ = '(.*)'$",
                     open('phdiff/version.py', 'r').read(),
                     re.MULTILINE).group(1)

HDIFFPATCH_SOURCES = [
    "HDiff/diff.cpp",
    "HDiff/private_diff/compress_detect.cpp",
    "HDiff/private_diff/suffix_string.cpp",
    "HDiff/private_diff/libdivsufsort/divsufsort.c",
    "HDiff/private_diff/libdivsufsort/divsufsort64.c",
    "HDiff/private_diff/limit_mem_diff/stream_serialize.cpp",
    "HDiff/private_diff/limit_mem_diff/digest_matcher.cpp",
    "HDiff/private_diff/limit_mem_diff/adler_roll.c",
    "HDiff/private_diff/bytes_rle.cpp",
    "HPatch/patch.c",
]

HDIFFPATCH_SOURCES = [
    "phdiff/HDiffPatch/libHDiffPatch/" + source
    for source in HDIFFPATCH_SOURCES
]
HDIFFPATCH_SOURCES += ["phdiff/phdiffpatch.cpp"]
HDIFFPATCH_SOURCES += ["phdiff/HDiffPatch/file_for_patch.c"]

setup(name='phdiff',
      version=find_version(),
      description='Binary delta encoding tools.',      
      author='IllayDevel',
      author_email='idevel@bk.ru',
      license='BSD',
      classifiers=[
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
      ],
      url='https://github.com/IllayDevel',
      packages=find_packages(exclude=['tests']),
      install_requires=[
          'humanfriendly',
          'bitstruct',
          'pyelftools',
          'zstandard',
          'lz4',
          'heatshrink2'
      ],
      ext_modules=[        
          Extension(name="phdiff.phdiffpatch", sources=HDIFFPATCH_SOURCES)
      ],
      test_suite="tests",
      entry_points={
          'console_scripts': ['phdiff=phdiff.__init__:_main']
      })
