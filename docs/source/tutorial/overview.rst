Overview
========

Ocean temperature and salinity profiles are distributed within hours of
being measured, long before an expert can look at them. Near-real-time quality
control (NRT QC) is the set of automated tests applied at that stage: they
catch the errors a machine can recognise on its own, such as an impossible
date, a position on land, a value outside any plausible ocean range, or a
spike between two neighbouring measurements. The resulting flags tell users
which values to trust before delayed-mode QC revisits the data.

``nrtqclib`` runs these tests (the Argo/CTD RTQC tests) on a Parquet file of
CTD profiles. For every observation it writes one flag column per test and a
final NRT flag per variable, using the IOC/Argo scheme: ``1`` (good), ``3``
(probably bad) and ``4`` (bad).

The Workflow
------------

A run starts from the NetCDF files distributed by Copernicus Marine and ends
with a flagged Parquet file. Two companion command-line tools prepare the
input:

.. code-block:: text

   NetCDF files
       |  ctddump: convert, merge and clean
       v
   Parquet file (one row per observation)
       |  seastamp: add the sea floor depth at each position
       v
   Parquet file + bathymetry column
       |  nrtqclib: run the QC tests
       v
   Parquet file + one flag column per test + temp_nrt_flag / psal_nrt_flag
   (+ a report comparing the new flags with the flags already in the file)

1. :doc:`ctddump <ctddump>` converts the Copernicus NetCDF files to Parquet,
   merges them into one file, and removes unusable and duplicate profiles.
2. :doc:`seastamp <seastamp>` adds a ``bathymetry`` column. Only one test
   needs it (the position on land test), so this step is optional.
3. :doc:`nrtqclib <running_nrt_qc>` runs the QC tests, driven by a YAML
   configuration file.

Basic Usage
-----------

Once the input file exists, a run takes three calls:

.. code-block:: python

   import nrtqclib as nq

   nq.write_config_template("~/aiqc_project/config/nrt_qc_config.yaml")
   # Edit the paths, the input file name and the regional ranges, then:
   config = nq.read_config("~/aiqc_project/config/nrt_qc_config.yaml")
   nq.run_nrt_qc(config)

Where ``aiqclib`` Fits In
-------------------------

The QC tests themselves are implemented in `aiqclib
<https://aiqclib.readthedocs.io>`_, the machine-learning library of the AIQC
project; ``nrtqclib`` is the pipeline that runs them, and it installs
``aiqclib`` as a dependency. The flag columns ``nrtqclib`` writes can then be
used as training features in ``aiqclib`` (see
:doc:`aiqclib:how-to/qc_items_as_features`). You do not need to know
``aiqclib`` to follow this tutorial.

Objectives
----------

By the end of this tutorial you will have:

* installed ``nrtqclib``, ``ctddump`` and ``seastamp``,
* built an input Parquet file from Copernicus NetCDF files,
* added the sea floor depth to it, and
* run NRT QC on it and read the flags and the comparison report.

.. tip::

   To try ``nrtqclib`` before setting up the two tools, download the
   example dataset described in :doc:`aiqclib:tutorial/input_data` and go
   straight to :doc:`running_nrt_qc`. It was produced by the same kind of
   pipeline, so everything on that page applies to it.

Each QC test has its own page under **QC Items**, with the reasoning behind
it and a diagram of what it flags; start at :doc:`../qc_items/overview`.

Next Steps
----------

Proceed to the next tutorial: :doc:`./installation`.
