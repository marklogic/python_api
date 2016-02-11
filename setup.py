from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import marklogic

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst')

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
    name='marklogic_python_api',
    version=marklogic.__version__,
    url='https://github.com/marklogic/python_api/',
    license='Apache Software License',
    author='Norman Walsh',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    author_email='norman.walsh@marklogic.com',
    description='MarkLogic Python API',
    long_description=long_description,
    packages=find_packages(exclude=['test']),
    install_requires=[
        'requests>=2.5.0',
        'requests_toolbelt>=0.6.0'
    ],
    include_package_data=True,
    platforms='any',
    test_suite='marklogic.test.test_marklogic',
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
