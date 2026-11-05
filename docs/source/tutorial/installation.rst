Step 1: Installation
====================

``nrtqclib`` is a Python package on PyPI and needs Python 3.12 or newer. It
installs ``aiqclib``, which provides the QC tests, as a dependency. The two
companion tools of the next steps, ``ctddump`` and ``seastamp``, are
standalone programs, installed on their own pages.

.. note::

   Install the package inside a virtual environment (``venv``, ``uv`` or a
   conda environment) to keep its dependencies apart from other projects and
   from the system Python.

Using pip
---------

.. code-block:: bash

   pip install nrtqclib

Using uv
--------

``uv`` creates the virtual environment and installs into it:

.. code-block:: bash

   # Create a virtual environment in .venv
   uv venv

   # Activate it (Linux/macOS)
   source .venv/bin/activate
   # On Windows: .venv\Scripts\activate

   uv pip install nrtqclib

Using conda or mamba
--------------------

``nrtqclib`` is **not on conda-forge**. Create the environment with conda or
mamba, then install the package into it with ``pip``:

.. code-block:: bash

   mamba create -n nrtqc -c conda-forge python=3.12 pip
   mamba activate nrtqc
   pip install nrtqclib

Checking the Installation
-------------------------

.. code-block:: bash

   python -c "import nrtqclib, aiqclib; print(nrtqclib.__version__, aiqclib.__version__)"

For Development
---------------

To work on ``nrtqclib`` itself, clone the repository and let ``uv`` install
the dependencies and the package in editable mode:

.. code-block:: bash

   git clone https://github.com/AIQC-Hub/nrtqclib.git
   cd nrtqclib
   uv sync
   uv run pytest

Setting Up the Project Directories
----------------------------------

The tutorial keeps its files under ``~/aiqc_project``, the same directory the
``aiqclib`` tutorials use, so the NRT QC output can feed them directly:

.. code-block:: bash

   mkdir -p ~/aiqc_project/config   # configuration files
   mkdir -p ~/aiqc_project/input    # the input Parquet file
   mkdir -p ~/aiqc_project/work     # intermediate files of ctddump
   mkdir -p ~/aiqc_project/data     # NRT QC output

Next Steps
----------

Proceed to the next tutorial: :doc:`./ctddump`.
