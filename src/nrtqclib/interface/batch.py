"""
Running NRT QC over several datasets.

:func:`run_batch` runs :func:`~nrtqclib.interface.nrtqc.run_nrt_qc` once per
dataset named in a table, selecting each dataset's set from one NRT QC config
file. It drives the ``aiqclib`` batch engine
(:func:`aiqclib.interface.batch.run_phases`), so the table format, skipping,
error handling and summary frame are the same as for ``aiqclib.run_batch``:

.. code-block:: text

   name       nrt_qc_set_name
   ar_ar      nrt_qc_ar_ar_0001
   bo_bo      nrt_qc_bo_bo_0001

The first column (or one called ``name``) identifies the dataset and the
``nrt_qc_set_name`` column gives the set to select. A blank cell skips that
dataset. The table may also be the one used for ``aiqclib.run_batch``, with
an extra ``nrt_qc_set_name`` column: other columns are ignored.
"""

from typing import Optional, Sequence, Union

import polars as pl

from aiqclib.interface.batch import Phase, run_phases

from nrtqclib.interface.config import read_config
from nrtqclib.interface.nrtqc import run_nrt_qc


#: The NRT QC phase handed to the ``aiqclib`` batch engine. It carries its own
#: config reader, since ``aiqclib.read_config`` does not read NRT QC files.
#: ``in_all`` is False because NRT QC produces flag columns that feed
#: ``aiqclib``'s prepare phase rather than being a step of it.
NRT_QC_PHASE = Phase(
    "nrt_qc",
    "nrt_qc_set_name",
    "nrt_qc_config",
    run_nrt_qc,
    in_all=False,
    config_reader=read_config,
)


def run_batch(
    table: Optional[Union[str, pl.DataFrame]] = None,
    *,
    nrt_qc_config: Optional[str] = None,
    names: Optional[Sequence[str]] = None,
    verbose: bool = False,
    continue_on_error: bool = False,
) -> pl.DataFrame:
    """
    Run the NRT QC pipeline for every dataset named in a table.

    Without a table, the pipeline runs once and the config file selects its
    own set (it must then hold a single set).

    :param table: Path to the dataset table (whitespace aligned, ``.tsv`` or
                  ``.csv``), or an already-loaded DataFrame. ``None`` runs
                  once without naming a set.
    :type table: Optional[Union[str, polars.DataFrame]]
    :param nrt_qc_config: The NRT QC configuration file. Required.
    :type nrt_qc_config: Optional[str]
    :param names: Run only these datasets, instead of every row. Requires a
                  table.
    :type names: Optional[Sequence[str]]
    :param verbose: Report each dataset as it starts, and pass the flag on to
                    :func:`run_nrt_qc`. Defaults to False.
    :type verbose: bool
    :param continue_on_error: When True, a failing dataset is recorded and the
                              batch carries on; when False the exception
                              propagates immediately. Defaults to False.
    :type continue_on_error: bool
    :raises ValueError: If ``nrt_qc_config`` is missing, the table lacks the
                        ``nrt_qc_set_name`` column, a requested name is not in
                        the table, or ``names`` is given without a table.
    :return: One row per dataset (see
             :data:`aiqclib.interface.batch.SUMMARY_SCHEMA`), with ``status``
             one of ``"ok"``, ``"skipped"`` or ``"failed"``.
    :rtype: polars.DataFrame

    :Example:

    .. code-block:: python

        import polars as pl
        import nrtqclib as nq

        summary = nq.run_batch(
            "datasets.tsv", nrt_qc_config="nrtqc.yaml", verbose=True
        )
        print(summary.filter(pl.col("status") == "failed"))
    """
    return run_phases(
        (NRT_QC_PHASE,),
        mode=NRT_QC_PHASE.name,
        config_files={NRT_QC_PHASE.config_argument: nrt_qc_config},
        table=table,
        names=names,
        verbose=verbose,
        continue_on_error=continue_on_error,
    )
