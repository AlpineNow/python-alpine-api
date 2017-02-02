.. Alpine SDK documentation master file, created by
   sphinx-quickstart on Thu Jan 26 11:36:41 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

API Reference
=============

A Python wrapper for the Alpine API. Here's a simple example to run an Alpine Workflow.::

    import api as AlpineAPI
    session = AlpineAPI.Alpine(host, port, username, password)
    process_id = session.workfile.run_workflow(workfile_id)
    results = session.workfile.download_workflow_results(workfile_id, process_id)

Requirements:

1. Python 2.7
2. Requests ???

Contents:

.. toctree::
   :maxdepth: 2

   Alpine
   Users
   Workspaces
   Workfiles
   Job
   Alpineobject


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

