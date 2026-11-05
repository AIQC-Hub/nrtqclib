Step 3: Adding the Sea Floor Depth with ``seastamp``
====================================================

The position on land test (RTQC4) checks that a profile was taken in the
ocean. To decide that, it needs the depth of the sea floor at the profile's
position, which is not part of the CTD data. `seastamp
<https://aiqc-hub.github.io/seastamp/introduction.html>`_ is the companion
command-line tool that looks it up: it reads the ``longitude`` and
``latitude`` of every row and appends a ``bathymetry`` column taken from the
`GEBCO <https://www.gebco.net/>`_ global bathymetry grid.

This step is **optional**. Without it, leave ``position_on_land`` out of the
configuration and every other test runs as usual. ``seastamp`` can add other
attributes too (distance to the coast, sea area name, nearest country), but
``nrtqclib`` uses only the depth.

Installing ``seastamp``
-----------------------

.. tabs::

   .. tab:: Prebuilt binary (recommended)

      Download the archive for your platform (Linux or macOS, x86_64 or
      arm64) from the `latest release
      <https://github.com/AIQC-Hub/seastamp/releases/latest>`_, unpack it,
      and put the ``seastamp`` executable on your ``PATH``. The binaries
      bundle HDF5 and netCDF, which the depth lookup needs.

      .. code-block:: bash

         seastamp --help

   .. tab:: crates.io

      Needs a Rust toolchain and, for the depth lookup, the HDF5/netCDF
      development headers:

      .. code-block:: bash

         # Ubuntu / Debian: sudo apt-get install libhdf5-dev libnetcdf-dev
         # macOS:           brew install hdf5
         cargo install seastamp

See the `seastamp installation guide
<https://aiqc-hub.github.io/seastamp/installation.html>`_ for building from
source.

Downloading the Bathymetry Grid
-------------------------------

The datasets are not bundled with the tool. The ``seastamp`` repository
ships a download script; fetch the GEBCO grid with:

.. code-block:: bash

   scripts/download_data.sh download gebco

The grid is several gigabytes, and the script resumes an interrupted
download. It unpacks the 2024 grid to
``./data/gebco/GEBCO_2024_sub_ice_topo.nc``, relative to the directory you
run it from (``--data DIR`` changes that, ``--gebco-year N`` fetches another
release). See the `seastamp data page
<https://aiqc-hub.github.io/seastamp/data.html>`_ for the other datasets
and options.

Adding the Column
-----------------

.. code-block:: bash

   seastamp depth ~/aiqc_project/input/nrt_bo.parquet \
     --data ./data/gebco/GEBCO_2024_sub_ice_topo.nc \
     --positive -o ~/aiqc_project/input/nrt_bo_depth.parquet

This reads the ``ctddump`` output of the previous step and writes a new file
next to it. All input columns are kept, and ``bathymetry`` is appended in
metres.

.. important::

   **Mind the sign.** GEBCO stores *elevation*, which is negative below sea
   level. ``--positive`` flips it, so the column reads as a depth: positive
   in the ocean, negative on land. That is the convention the
   ``position_on_land`` test assumes by default (``positive_depth: true``).

   Without ``--positive`` the ocean is negative, and the test must be told so
   with ``positive_depth: false``. Getting this wrong inverts the test: every
   ocean profile would fail and every land profile would pass.

====================== ================== ===================================
``seastamp depth``     ocean values       ``position_on_land`` params
====================== ================== ===================================
with ``--positive``    ``bathymetry > 0`` defaults (nothing to set)
without ``--positive`` ``bathymetry < 0`` ``positive_depth: false``
====================== ================== ===================================

A position off the grid gets a null ``bathymetry``, and a null passes the
test: an unknown depth is not evidence of land.

Checking the Result
-------------------

Before enabling the test, confirm the sign on your own data. Profiles taken
at sea should have almost entirely positive values:

.. code-block:: python

   import polars as pl

   df = pl.read_parquet("~/aiqc_project/input/nrt_bo_depth.parquet")
   print(df.select(
       (pl.col("bathymetry") > 0).mean().alias("share_positive"),
       pl.col("bathymetry").min().alias("min"),
       pl.col("bathymetry").max().alias("max"),
   ))

A share close to 0 instead of 1 means the sign is the other way round.

Next Steps
----------

Proceed to the next tutorial: :doc:`./running_nrt_qc`.
