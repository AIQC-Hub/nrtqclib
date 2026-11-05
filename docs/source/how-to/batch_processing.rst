Running a Batch of Datasets
===========================

``run_batch`` runs NRT QC once per dataset named in a table, selecting each
dataset's set from one configuration file:

.. code-block:: python

   import nrtqclib as nq

   summary = nq.run_batch(
       "datasets.txt",
       nrt_qc_config="nrt_qc_config.yaml",
       verbose=True,
   )

It uses the ``aiqclib`` batch engine, so the table format, skipping, failure
handling and summary frame are the same as for ``aiqclib.run_batch``: see
:doc:`aiqclib:how-to/batch_processing` for the details. This page covers what
is specific to NRT QC.

The Dataset Table
-----------------

The first column (or one called ``name``) names each dataset; the
``nrt_qc_set_name`` column gives the ``nrt_qc_sets`` entry to select:

.. code-block:: text

   # NRT region sets
   name       nrt_qc_set_name
   ar_ar      nrt_qc_ar_ar_0001
   bo_bo      nrt_qc_bo_bo_0001
   cora_mo    nrt_qc_cora_mo_0001

Other columns are ignored, so the table used for ``aiqclib.run_batch`` can
carry an ``nrt_qc_set_name`` column and drive both packages. A blank cell
skips that dataset. A ``.tsv`` or ``.csv`` extension is read by that
delimiter, and a Polars DataFrame can be passed in place of a path.

.. note::

   The NRT QC guide suggests one configuration file per region, because the
   regional ranges differ. For a batch, put the regions in **one** file
   instead: ``qc_item_sets`` is a top-level list, so it can hold one item set
   per region, with one ``nrt_qc_sets`` entry each referencing its own. The
   ``nrt_qc_set_name`` column then names the entry per row.

Without a table, the pipeline runs once and the configuration file selects
its own set, which works when the file holds a single set:

.. code-block:: python

   summary = nq.run_batch(nrt_qc_config="nrt_qc_config.yaml")

Running Part of a Table, and Failures
-------------------------------------

``names`` restricts a run to particular datasets. ``continue_on_error=True``
records a failing dataset in the summary and carries on, instead of raising:

.. code-block:: python

   summary = nq.run_batch(
       "datasets.txt",
       nrt_qc_config="nrt_qc_config.yaml",
       names=["bo_bo"],
       continue_on_error=True,
   )

.. important::

   With ``continue_on_error=True`` the batch always ends normally, so the
   summary (one row per dataset, with ``status`` ``"ok"``, ``"skipped"`` or
   ``"failed"`` and the error message) is the only record of what failed.
   Check it before treating a run as successful.

.. _batch-nrt-qc:

NRT QC and the Training Pipeline
--------------------------------

``aiqclib.run_batch(mode="all")`` runs prepare, train and classify, each
consuming what the previous one wrote. NRT QC does not sit in that chain: it
produces flag columns that are an *input* to the prepare phase, usable as
training features (see :doc:`aiqclib:how-to/qc_items_as_features`), rather
than a step of it. Running it on every retrain would redo the QC on data that
has not changed.

So the usual order is to run the QC once when the input data changes, then
the training pipeline as often as you like:

.. code-block:: python

   import aiqclib as aq
   import nrtqclib as nq

   nq.run_batch("datasets.txt", nrt_qc_config="nrt_qc_config.yaml")

   aq.run_batch(
       "datasets.txt",
       mode="all",
       prepare_config="prepare_config.yaml",
       training_config="training_config.yaml",
       classification_config="classification_config.yaml",
   )

.. note::

   Migrating from ``aiqclib``: ``aq.run_batch(table, mode="nrt_qc",
   nrt_qc_config=...)`` becomes ``nq.run_batch(table, nrt_qc_config=...)``.
   There is no ``mode`` argument, and every argument after the table is
   keyword-only.
