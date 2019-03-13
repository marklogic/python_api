from __future__ import print_function
from setuptools import setup, find_packages
import io

import marklogic

def read(*filenames, **kwargs):
    """Read and merge content of several files"""
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as infile:
            buf.append(infile.read())
    return sep.join(buf)

setup(
    name='marklogic_python_api',
    version=marklogic.__version__,
    url='https://github.com/marklogic/python_api/',
    license='Apache Software License',
    author='Norman Walsh',
    author_email='norman.walsh@marklogic.com',
    description='MarkLogic Python API',
    long_description=read('README.rst'),
    packages=find_packages(),
    install_requires=[
        'requests>=2.21.0',
        'requests_toolbelt>=0.9.1'
    ],
    include_package_data=True,
    platforms='any',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=['Programming Language :: Python', \
        'Development Status :: 3 - Alpha', \
        'Natural Language :: English', \
        'Environment :: Console', \
        'Intended Audience :: Developers', \
        'License :: OSI Approved :: Apache Software License', \
        'Operating System :: OS Independent', \
        'Topic :: Software Development :: Libraries :: Python Modules' \
        ],
)
