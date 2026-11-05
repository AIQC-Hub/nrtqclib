"""
nrtqclib Interface Module
=========================

Near-real-time quality control (NRT QC) for CTD ocean profiles. The QC items
themselves live in :mod:`aiqclib`; this package runs them as an NRT pipeline.

Attributes:
    __version__ (str): The version of the nrtqclib library.
"""

from importlib.metadata import version, PackageNotFoundError

from nrtqclib.interface.nrtqc import run_nrt_qc

try:
    __version__ = version("nrtqclib")
except PackageNotFoundError:
    __version__ = "unknown"


__all__ = [
    "run_nrt_qc",
]
