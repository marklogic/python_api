# MarkLogic Python API

This is a (relatively low-level) Python(3) API to the MarkLogic REST
Management API. It may grow to support the Client API as well, over time,
and it will certainly grow higher-level APIs.

The API aims to provide complete coverage of what's in the MarkLogic
REST API in idiomatic Python.

## Features

-  Creation and configuration of databases, forests, servers, hosts,
   users, roles, permissions, and privileges.

## Getting Started

1. Download and install MarkLogic (http://developer.marklogic.com/products)
3. Checkout the MarkLogic python package from
   http://github.com/marklogic/python-api
4. Install using ``easy_install`` (``easy_install /path/to/python-api``)

At this point you should be able to script away. In the near future
you’ll be able to directly install using easy_install without first
checking out the project.

## Running Tests

To run tests, edit the `test/resources.py` and `tests/settings.py`
files to match your MarkLogic setup. The tests reference these values
to connect with your MarkLogic server.

## Credits

This library began as a project by Paul Hoehne, to whom we are
indebted.

