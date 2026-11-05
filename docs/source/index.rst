nrtqclib
========

``nrtqclib`` applies automated near-real-time quality control (NRT QC) tests
(Argo/CTD RTQC tests) to temperature and salinity profiles, producing
per-item flag columns and a final NRT flag per variable.

The QC items are implemented in `aiqclib <https://aiqclib.readthedocs.io>`_,
where the same tests can also be used as training features for the
machine-learning models.

.. toctree::
   :maxdepth: 2
   :caption: How-to guides

   how-to/nrt_qc

.. toctree::
   :maxdepth: 2
   :caption: Configuration

   configuration/nrtqc
