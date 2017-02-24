.. Alpine SDK documentation master file, created by
   sphinx-quickstart on Thu Jan 26 11:36:41 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

API Reference
=============

Welcome to the official Python library for the Alpine API. In this first release we've focused on a subset of the full
API that we feel users will most frequently use.

This library can be used to automate, add or simplify functionality of Alpine.

Example request to run an Alpine workflow::

    import api as AlpineAPI
    session = AlpineAPI.Alpine(host, port, username, password)
    process_id = session.workfile.run(workfile_id)
    session.workfile.wait_until_finished(process_id)
    results = session.workfile.download(workfile_id, process_id)

Contents

.. toctree::
   :maxdepth: 2

   APIReference
   Introduction
   Advanced Usage

Requirements:

1. Python 2.7
2. Requests 2.12.4

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

