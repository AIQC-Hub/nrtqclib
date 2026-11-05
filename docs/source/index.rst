Welcome to the ``nrtqclib`` documentation!
==========================================

``nrtqclib`` applies automated near-real-time quality control (NRT QC) tests
(the Argo/CTD RTQC tests) to temperature and salinity profiles. For every
observation it writes one flag per test and a final NRT flag per variable,
and it can compare its verdicts with the flags already in the data. It is a
component of the AIQC project.

.. note::
   New to ``nrtqclib``? The :doc:`tutorial/overview` walks from Copernicus
   NetCDF files to a flagged Parquet file. To see what each test checks,
   start at :doc:`qc_items/overview`.

Workflow of ``nrtqclib``
------------------------

1.  **Prepare the input:** convert Copernicus NetCDF files to Parquet with
    `ctddump <https://aiqc-hub.github.io/ctddump/introduction.html>`_, and
    optionally add the sea floor depth with `seastamp
    <https://aiqc-hub.github.io/seastamp/introduction.html>`_.
2.  **Configure:** choose the QC items and their parameters in a YAML file,
    one set per region.
3.  **Run:** ``nq.run_nrt_qc`` writes the flags and the comparison reports;
    ``nq.run_batch`` runs several regions in one call.

The QC items are implemented in `aiqclib <https://aiqclib.readthedocs.io>`_,
where the same tests can also be used as training features for the
machine-learning models.

Project links
-------------

  - `GitHub Repository <https://github.com/AIQC-Hub/nrtqclib>`_
  - `Issue Tracker <https://github.com/AIQC-Hub/nrtqclib/issues>`_
  - `PyPI <https://pypi.org/project/nrtqclib/>`_

----------

These tutorials take you step by step from raw data to NRT QC flags. If you
are new to ``nrtqclib``, start here.

.. toctree::
   :maxdepth: 2
   :caption: 📘 Getting Started

   tutorial/overview
   tutorial/installation
   tutorial/ctddump
   tutorial/seastamp
   tutorial/running_nrt_qc

----------

Practical guides to the options of the pipeline.

.. toctree::
   :maxdepth: 2
   :caption: 💡 How-To Guides

   how-to/nrt_qc
   how-to/batch_processing

----------

Reference for every parameter of the YAML configuration file.

.. toctree::
   :maxdepth: 2
   :caption: ⚙️ Configuration

   configuration/nrtqc

----------

What each QC test checks, why it matters, and how it decides.

.. toctree::
   :maxdepth: 1
   :caption: 🔍 QC Items

   qc_items/overview
   qc_items/impossible_date
   qc_items/impossible_location
   qc_items/position_on_land
   qc_items/global_range
   qc_items/regional_range
   qc_items/pressure_increasing
   qc_items/spike
   qc_items/gradient
   qc_items/digit_rollover
   qc_items/stuck_value
   qc_items/density_inversion
   qc_items/temp_to_psal

----------

For in-depth information on specific functions, classes, and methods, consult
the API documentation.

.. toctree::
   :maxdepth: 4
   :caption: 🧩 API Reference

   api/modules
