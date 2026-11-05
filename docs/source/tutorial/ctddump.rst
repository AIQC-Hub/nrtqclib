Step 2: Converting CTD Data with ``ctddump``
============================================

``nrtqclib`` reads a single Parquet file holding one row per observation.
Copernicus Marine distributes CTD profiles as NetCDF files, one per platform
and period. `ctddump <https://aiqc-hub.github.io/ctddump/introduction.html>`_
is the companion command-line tool that turns a directory of those files into
the Parquet file ``nrtqclib`` expects: it converts, merges, numbers the
profiles and observations, and removes unusable and duplicate profiles.

``ctddump`` reads the Near Real Time products for the Arctic (``nrt_ar``),
Baltic (``nrt_bo``), Mediterranean (``nrt_mo``) and Global (``nrt_gl``) seas,
the CORA reanalysis (``cora``, ``cora_legacy``), and other NetCDF files
described by a mapping file (``generic``).

Installing ``ctddump``
----------------------

.. tabs::

   .. tab:: Prebuilt binary (recommended)

      The release archives bundle HDF5 and netCDF, so nothing else needs to
      be installed. Download the archive for your platform (Linux or macOS,
      x86_64 or arm64) from the `latest release
      <https://github.com/AIQC-Hub/ctddump/releases/latest>`_, unpack it,
      and put the ``ctddump`` executable on your ``PATH``:

      .. code-block:: bash

         tar -xzf ctddump-<version>-<target>.tar.gz
         mkdir -p ~/.local/bin
         mv ctddump-<version>-<target>/ctddump ~/.local/bin/
         ctddump --version

   .. tab:: crates.io

      Needs a Rust toolchain and the HDF5/netCDF development headers:

      .. code-block:: bash

         # Ubuntu / Debian: sudo apt-get install libhdf5-dev libnetcdf-dev
         # macOS:           brew install hdf5
         cargo install ctddump

See the `ctddump installation guide
<https://aiqc-hub.github.io/ctddump/installation.html>`_ for checksums and
building from source.

Building the Input File
-----------------------

Starting from a directory of NetCDF files, the commands below produce
``~/aiqc_project/input/nrt_bo.parquet``. The example uses the Baltic product;
replace ``nrt_bo`` with the subcommand of your region.

.. code-block:: bash

   W=~/aiqc_project/work

   # 1. Convert every NetCDF file in the tree to Parquet (in parallel)
   ctddump batch convert nrt_bo --output $W/pq /path/to/netcdf

   # 2. Merge them into one file, numbering profile_no and observation_no
   ctddump concat convert $W/pq $W/merged.parquet

   # 3. Drop profiles whose temp, psal or pres is entirely missing
   ctddump dropna $W/merged.parquet $W/na.parquet

   # 4. Drop profiles flagged bad by the profile-level QC (time_qc / position_qc)
   ctddump dropqc $W/na.parquet $W/qc.parquet

   # 5. Mark duplicate profiles, then keep one profile per duplicate group
   ctddump markdup $W/qc.parquet $W/marked.parquet $W/duplicates.tsv
   ctddump dedup $W/marked.parquet ~/aiqc_project/input/nrt_bo.parquet

.. note::

   ``batch convert`` may print ``HDF5-DIAG`` messages about attributes it
   cannot find (such as ``_QuantizeBitRoundNumberOfSignificantBits``). These
   come from the HDF5 library probing optional attributes and are harmless
   when the command finishes with exit status 0.

What each step does, and why:

``batch convert``
   Writes one Parquet file per NetCDF file. ``--threads N`` caps the number
   of workers.

``concat convert``
   Merges the files and numbers the profiles and observations, which is
   where the ``profile_no`` and ``observation_no`` columns ``nrtqclib``
   needs come from. It also sorts each profile by pressure and drops rows
   whose pressure is missing (``--keep-na-pres`` keeps them).

``dropna``
   A profile with no temperature, salinity or pressure at all has nothing to
   test.

``dropqc``
   Removes the profiles the data provider already flagged as having a bad
   date or position. **Skip this step** if you want the impossible date and
   impossible location tests to see those profiles, for example to compare
   their verdicts with the provider's.

``markdup`` / ``dedup``
   The same profile often arrives more than once, from different platforms
   or file versions. ``markdup`` lists the duplicates in a TSV file for
   review; ``dedup`` keeps the profile with the most observations from each
   group.

Checking the Result
-------------------

``ctddump report`` summarises a file per platform, per profile, or as a
whole:

.. code-block:: bash

   ctddump report parquet --level global --format text ~/aiqc_project/input/nrt_bo.parquet

The file has one row per observation, with the columns ``nrtqclib`` needs:

======================= ==========================================================
Column                  Used for
======================= ==========================================================
``platform_code``       identifies the platform (part of the profile key)
``profile_no``          identifies the profile within a platform
``observation_no``      the order of the observations within a profile
``profile_timestamp``   the impossible date test
``longitude``,          the impossible location test
``latitude``
``pres``                every depth-dependent test, and the pressure test itself
``temp``, ``psal``      the variables under test
``temp_qc``,            the provider's existing NRT flags, compared with the new
``psal_qc``             flags in the report (optional)
======================= ==========================================================

.. _ctddump-nan:

Turning NaN Into Null
---------------------

``ctddump`` stores a missing measurement as ``NaN``. The QC items treat a
*null* as missing and let it pass, but they read ``NaN`` as a value larger
than any other, so it fails the range, spike, gradient and digit rollover
tests. Convert ``NaN`` to null before running NRT QC:

.. code-block:: python

   import polars as pl

   path = "~/aiqc_project/input/nrt_bo.parquet"
   df = pl.read_parquet(path)
   df.with_columns(pl.col(pl.Float32, pl.Float64).fill_nan(None)).write_parquet(path)

Without this, every missing temperature or salinity gets flag ``4`` in
``temp_nrt_flag`` / ``psal_nrt_flag``, and ``temp_to_psal`` passes the
temperature failures on to salinity. On ctddump's five Baltic test files,
64 missing temperatures turned into 1,366 observations flagged 4 instead of
none. The comparison report is skewed accordingly.

.. note::

   ``ctddump`` writes QC flags as single-character strings (``"1"``,
   ``"4"``, ``""`` for missing) where other sources use integers. The
   comparison step of ``nrtqclib`` reads both, so the configuration is the
   same either way.

For every option of every command, see the `ctddump documentation
<https://aiqc-hub.github.io/ctddump/>`_.

Next Steps
----------

The file is ready for every test except the position on land test, which
needs the sea floor depth at each position. Add it in the next step, or skip
to :doc:`./running_nrt_qc` and leave that test out.

Proceed to the next tutorial: :doc:`./seastamp`.
