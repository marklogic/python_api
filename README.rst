====================
MarkLogic Python API
====================

This is a (relatively low-level) Python(3) API to the MarkLogic REST
Management API. It may grow to support the Client API as well, over time,
and it will certainly grow higher-level APIs.

The API aims to provide complete coverage of what's in the MarkLogic
REST API in idiomatic Python.

Churn warning
=============

Several aspects of the API design are still in flux. Some
inconsistencies are present. If you write scripts based on it, you'll
probably have to fix them after each update. Apologies, in advance,
and thanks for your feedback.

Some aspects of the current API rely on server features that have not
yet been released to the public. In particular, it’s likely that
attempts to work with forest properties will not work with the current
public releases of MarkLogic server.

The installer has not been widely tested. Feedback welcome.

Features
========

* Creation and configuration of clusters, groups, databases, forests,
  servers, hosts, users, roles, permissions, and privileges.
* A sample command-line utility
* Several example scripts
* Some rather crude at the moment API docs.

Getting Started
===============

1. Download and install MarkLogic (http://developer.marklogic.com/products)
2. Install using ``pip`` (``pip3 install marklogic_python_api``)
   Note that you must be using Python3!
3. Checkout the MarkLogic python package from
   http://github.com/marklogic/python_api

At this point you should be able to script away.

Pythonistas may find it useful to simply create a virtualenv for the
project and run `python setup.py install`.

Running Tests
=============

To run tests, edit the `test/resources.py` and `tests/settings.py`
files to match your MarkLogic setup. The tests reference these values
to connect with your MarkLogic server.

Credits
=======

This library began as a project by Paul Hoehne, to whom we are
indebted.
