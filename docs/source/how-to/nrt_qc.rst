Tuning NRT QC Runs
==================

This guide covers the choices you make once a basic run works: how to handle
several regions, how much weight each QC item gets in the final flag, and how
to read the comparison against the flags already in your data. For a first
run, start with the :doc:`../tutorial/overview`; for what each item checks,
see :doc:`../qc_items/overview`.

.. note::

   Migrating from ``aiqclib``: ``aq.run_nrt_qc``, ``aq.read_config`` and
   ``aq.read_config_template("nrt_qc")`` become ``nq.run_nrt_qc``,
   ``nq.read_config`` and ``nq.read_config_template`` with the same
   arguments, minus ``stage``. ``aq.write_config_template(path,
   stage="nrt_qc")`` becomes ``nq.write_config_template(path)``. The pipeline,
   configuration format and outputs are unchanged.

Handling Regions
----------------

Some items depend on the region, most of all the regional range test, which
has no defaults. ``nrtqclib`` does not detect the region from the
coordinates: each run uses the parameters of the set it selects, so a region
is expressed as its own ``qc_item_sets`` entry with its own ranges, and its
own ``nrt_qc_sets`` entry that uses it.

There are two ways to organise that:

* **One configuration file per region** (Arctic, Baltic, Mediterranean, ...),
  each holding a single set. The files share their structure and differ only
  in the region-dependent parameters. Run each with ``nq.run_nrt_qc``.
* **One file holding every region**, with one ``nrt_qc_sets`` entry per
  region, run by ``nq.run_batch`` from a table that names the set for each
  dataset. This is the better choice once there are more than a few regions.

.. code-block:: python

   summary = nq.run_batch(
       "datasets.txt",
       nrt_qc_config="nrt_qc_config.yaml",
       verbose=True,
   )

See :doc:`batch_processing` for the table format, and :ref:`batch-nrt-qc` for
how this fits with ``aiqclib``'s training batch.

.. _nrtqc-fail-flag:

Softening a Test to "Probably Bad"
----------------------------------

A failing item writes flag ``4`` (bad) by default. ``fail_flag: 3`` makes it
write ``3`` (probably bad) instead:

.. code-block:: yaml

   qc_item_sets:
     - name: qc_item_set_1
       items:
         - name: global_range
         - name: gradient
           fail_flag: 3
         - name: position_on_land
           fail_flag: 3

Use it for a test that is informative but not conclusive on its own: one
that also fires on real features of your data (a gradient test in a region
with sharp thermoclines), or one whose input is approximate (a position on
land test near the coast, where the bathymetry grid is coarse).

What changes, and what does not:

* The final flag is the most severe item flag, so an observation that only a
  softened item fails ends up ``3``. If another item fails it with ``4``, it
  stays ``4``.
* ``temp_to_psal`` copies the final temperature flag with its severity, so a
  softened temperature failure reaches salinity as ``3``. ``fail_flag`` does
  not apply to ``temp_to_psal`` itself.
* Only ``3`` and ``4`` are accepted; any other value fails the configuration
  check.
* In the comparison report, the agreement metrics and the ``item_breakdown``
  rows count any flag above ``1`` as a failure, so they do not change. The
  ``contingency`` and ``item_breakdown_contingency`` rows show the ``3``.

.. _nrtqc-final-flag-guide:

Choosing Which Items Decide the Final Flag
------------------------------------------

By default every enabled item feeds the final ``{variable}_nrt_flag``.
``include_in_final_flag: false`` keeps an item running while leaving it out
of that decision:

.. code-block:: yaml

   qc_item_sets:
     - name: qc_item_set_1
       items:
         - name: spike
         - name: stuck_value
           include_in_final_flag: false

The item still runs and its column (``{variable}_qc_stuck_value``) is still
written, so the output has the same columns either way; only
``{variable}_nrt_flag`` differs. The comparison report also covers every
item regardless, which is the point: run a new or doubtful test this way,
check its ``item_breakdown`` rows against the existing flags, and include it
once it behaves.

``fail_flag`` and ``include_in_final_flag`` are two steps on the same scale:
``fail_flag: 3`` lets the test lower the final flag to "probably bad", and
``include_in_final_flag: false`` lets it record its verdict without affecting
the final flag at all.

Two consequences are worth knowing. Excluding an item from **temperature**
also removes it from what ``temp_to_psal`` propagates, because that item
reads the final ``temp_nrt_flag`` rather than the item columns. And
excluding ``temp_to_psal`` itself still writes ``psal_qc_temp_to_psal`` but
leaves ``psal_nrt_flag`` alone.

Comparing Against Existing Flags
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
