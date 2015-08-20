from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import python_api

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.adoc')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='python_api',
    version=python_api.__version__,
    url='https://github.com/marklogic/python_api/',
    license='Apache Software License',
    author='Norman Walsh',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    author_email='norman.walsh@marklogic.com',
    description='MarkLogic Python API',
    long_description=long_description,
    packages=find_packages("python_api"),
    package_dir = {'':'python_api'},
    install_requires=[
        'requests>=2.5.0'
    ],
    include_package_data=True,
    platforms='any',
    test_suite='python_api.test.test_python_api',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)
