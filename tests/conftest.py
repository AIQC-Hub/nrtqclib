"""Shared pytest fixtures for the nrtqclib test suite.

The path fixtures and ``nrtqc_config_001`` are the NRT QC subset of
aiqclib's ``tests/conftest.py``.

Test output files go under ``DATA_DIR / "test"`` (gitignored). Use the
``test_output_dir`` fixture and clean up manually with ``os.remove`` so
commenting out the cleanup lets you inspect outputs after a failure.
"""

from pathlib import Path

import pytest

from nrtqclib.config.nrtqc_config import NRTQCConfig


TESTS_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = TESTS_DIR / "data"
CONFIG_DIR: Path = DATA_DIR / "config"
INPUT_DIR: Path = DATA_DIR / "input"
TEST_OUTPUT_DIR: Path = DATA_DIR / "test"


@pytest.fixture
def tests_dir() -> Path:
    """Absolute path to the ``tests/`` directory."""
    return TESTS_DIR


@pytest.fixture
def data_dir() -> Path:
    """``tests/data/``: root of all test fixtures."""
    return DATA_DIR


@pytest.fixture
def config_dir() -> Path:
    """``tests/data/config/``: YAML config files."""
    return CONFIG_DIR


@pytest.fixture
def input_dir() -> Path:
    """``tests/data/input/``: raw pre-pipeline input data."""
    return INPUT_DIR


@pytest.fixture
def test_output_dir() -> Path:
    """``tests/data/test/``: destination for test-generated output files."""
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_OUTPUT_DIR


@pytest.fixture
def nrtqc_config_001() -> NRTQCConfig:
    """NRT QC config from the bundled template, pointed at the test fixture.

    The bundled ``template:nrt_qc_sets`` is loaded and its paths are
    redirected in-memory: input to the standard test parquet, outputs under
    ``TEST_OUTPUT_DIR / "nrt_qc"``.
    """
    config = NRTQCConfig("template:nrt_qc_sets")
    config.select("nrt_qc_0001")
    config.data["path_info"]["common"]["base_path"] = str(TEST_OUTPUT_DIR / "nrt_qc")
    config.data["path_info"]["input"]["base_path"] = str(INPUT_DIR)
    config.data["input_file_name"] = "nrt_cora_bo_test.parquet"
    return config
