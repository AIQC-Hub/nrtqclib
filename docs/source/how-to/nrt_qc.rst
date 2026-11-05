Running Near-Real Time Quality Control (NRT QC)
===============================================

The NRT QC module applies the automated real-time QC tests recommended for
temperature and salinity profiles (Argo/CTD RTQC tests) to an input dataset
and writes the original parquet enriched with:

* **one flag column per QC item**, e.g. ``temp_qc_spike`` or
  ``qc_impossible_date``, usable directly as training features, and
* **a final NRT flag per variable**: ``temp_nrt_flag`` / ``psal_nrt_flag``,
  the most severe flag among the variable's applicable item columns.

Flags follow the IOC/Argo scheme: 1 (good), 3 (probably bad), 4 (bad).

Quick start
-----------

.. code-block:: python

   import nrtqclib as nq

   nq.write_config_template("/path/to/nrt_qc_config.yaml")
   # Edit the paths, variables, and QC items in the YAML, then:
   config = nq.read_config("/path/to/nrt_qc_config.yaml")
   nq.run_nrt_qc(config)

``nq.read_config_template()`` returns the same template as a configuration
object, and ``print(config)`` summarizes what a configuration will run.

.. note::

   Migrating from ``aiqclib``: ``aq.run_nrt_qc``, ``aq.read_config`` and
   ``aq.read_config_template("nrt_qc")`` become the ``nq.`` functions above
   with the same arguments, minus ``stage``.
   ``aq.write_config_template(path, stage="nrt_qc")`` becomes
   ``nq.write_config_template(path)``. The pipeline, configuration format and
   outputs are unchanged.

.. _nrt-qc-items:

The QC items
------------

``aiqclib`` provides twelve QC items. Eleven implement the Argo/CTD
real-time tests (RTQC2 to RTQC14); ``temp_to_psal`` is the propagation rule
from the NRT QC recommendation document rather than a numbered test. An item
runs only when it is listed in the ``qc_item_sets`` section of the
configuration file.

Each item has its own page, explaining why the check matters and what it
flags, with a diagram: start at :doc:`../qc_items/overview`.

For the output column names, the full default parameters, and the YAML
syntax for overriding them, see :doc:`../configuration/nrtqc`.

One configuration file per region
---------------------------------

Some tests are region dependent (most notably the **regional range** test).
Instead of detecting the region from coordinates, prepare **one configuration
file per region** (e.g. Arctic, Baltic, Mediterranean): the files share the
same structure and differ only in region-dependent parameters such as the
regional ranges or the density inversion threshold.

Choosing which items decide the final flag
------------------------------------------

By default every enabled item feeds the aggregated
``{variable}_nrt_flag``. An item can be kept running while being left out of
that aggregation:

.. code-block:: yaml

   qc_item_sets:
     - name: qc_item_set_1
       items:
         - name: spike
         - name: stuck_value
           include_in_final_flag: false

The item still runs and ``{variable}_qc_stuck_value`` is still written, so
the output columns are unchanged; only ``{variable}_nrt_flag`` differs. Use
it when a test is worth recording but too aggressive to gate on, or when you
want to measure a test's behaviour (via the comparison report, which still
covers every item) before letting it affect the verdict.

Two consequences are worth knowing. Excluding an item from **temperature**
also removes it from what ``temp_to_psal`` propagates, because that item
reads the aggregated ``temp_nrt_flag`` rather than the raw columns. And
excluding ``temp_to_psal`` itself still writes ``psal_qc_temp_to_psal``
while leaving ``psal_nrt_flag`` alone.

See :ref:`nrtqc-final-flag-items` for the reference entry.

Temperature-to-salinity propagation
-----------------------------------

When salinity is computed from temperature and conductivity, a temperature
flagged 4 (or 3) corrupts the salinity too. Enabling the ``temp_to_psal``
item propagates the final temperature flag onto salinity with its severity,
recorded in its own ``psal_qc_temp_to_psal`` column so the propagation stays
traceable. Datasets with independently measured salinity simply omit the item
entirely, or keep it for traceability with
``include_in_final_flag: false``.

Comparing against existing flags
--------------------------------

When the input already carries NRT QC flags (e.g. ``temp_qc``, ``psal_qc``),
give each variable its ``flag`` column in the ``qc_variable_sets`` section:

.. code-block:: yaml

   qc_variable_sets:
     - name: qc_variable_set_1
       variables:
         - name: temp
           flag: temp_qc
           pos_flag_values: [ 4, 6, 7 ]  # optional: for agreement metrics
           neg_flag_values: [ 1 ]

``run_nrt_qc`` then writes one comparison report per variable
(``nrt_qc_flag_comparison_{variable}.tsv``) containing a contingency table
of existing vs new flag values, binary agreement metrics (accuracy,
precision, recall; only when the pos/neg flag values are given), and two
per-item breakdowns showing which items drive the disagreements. Variables
without a ``flag`` are skipped; omit all flags to skip the comparison step
entirely.

The two breakdowns count the same pairs of observations in different ways.
``item_breakdown`` asks whether the item failed at all, giving one row per
item and existing flag value, with the percentage taken within that value
("the item flagged 3% of the observations the input calls good").
``item_breakdown_contingency`` keeps the item's own flag value instead of
reducing it to pass or fail, giving one row per item and pair of values,
with the percentage taken over the whole variable as in the main
contingency table. Use the second when an item distinguishes suspect from
bad, or when the first shows a disagreement and the question is how severe
the item called it.

The existing flag column may hold integers, strings or floats, and the
configured values may be written as ``4`` or as ``"4"`` (see
:ref:`qc-flag-columns`). Existing flags that are missing or unreadable get
their own row in the contingency table, so they stay visible instead of being
folded into a real flag value; the agreement metrics count only the values
listed in ``pos_flag_values`` / ``neg_flag_values``. The input's flag columns
are written to the output unchanged, whatever type they use.

Running several regions at once
-------------------------------

``run_batch`` drives NRT QC over a table of datasets:

.. code-block:: python

   summary = nq.run_batch(
       "datasets.txt",
       nrt_qc_config="nrt_qc_config.yaml",
       verbose=True,
   )

Each row's ``nrt_qc_set_name`` names the set to select, so one configuration
file holding one entry per region replaces the per-region files suggested
above. See :doc:`batch_processing` for the table format, and
:ref:`batch-nrt-qc` for how this fits with ``aiqclib``'s training batch.

Using QC items as training features
-----------------------------------

Every QC item is an ordinary feature class registered under a
``qc_``-prefixed name (``qc_spike``, ``qc_global_range``, …), so the flag
columns can also be produced inside the Dataset Preparation pipeline and used
as model inputs. See :doc:`aiqclib:how-to/qc_items_as_features` for how to configure that,
and for the two items that need extra care there.
