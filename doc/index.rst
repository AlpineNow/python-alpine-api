Python wrapper for the Alpine API
=================================

Welcome to the official Python library for the Alpine API. In this first release we've focused on a subset of the full
API that we feel users will most frequently use.

This library can be used to automate, add or simplify functionality of Alpine.

Documentation (and examples):
   http://python-alpine-api.readthedocs.io/

Source code:
   https://github.com/AlpineNow/python-alpine-api

Python Package Index:
   https://pypi.python.org/pypi/alpine

Installation::

   pip install alpine

License:
   MIT. See




API Reference
=============

Welcome to the official Python library for the Alpine API. In this first release we've focused on a subset of the full
API that we feel users will most frequently use.

This library can be used to automate, add or simplify functionality of Alpine.

Example request to run an Alpine workflow::

    >>> import alpine as AlpineAPI
    >>> session = AlpineAPI.APIClient(host, port, username, password)
    >>> process_id = session.workfile.process.run(workfile_id)
    >>> session.workfile.process.wait_until_finished(process_id)
    >>> results = session.workfile.process.download(workfile_id, process_id)

Contents

.. toctree::
   :maxdepth: 2

   APIReference
   Introduction
   Advanced Usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

