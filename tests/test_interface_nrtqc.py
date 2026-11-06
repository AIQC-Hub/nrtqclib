"""Unit tests for the public NRT QC interface.

Covers ``run_nrt_qc`` end to end on the CTD fixture (with and without the
comparison step) and the config template/read round trip via the public
``write_config_template`` / ``read_config`` functions.
"""

import inspect
import os

import polars as pl

import nrtqclib as nq
from nrtqclib.config.nrtqc_config import NRTQCConfig


def _output_paths(config) -> dict:
    """The file paths the pipeline writes, keyed by kind."""
    paths = {
        "qc": config.get_full_file_name("qc", "nrt_qc_flags.parquet"),
        "output": config.get_full_file_name("concat", "nrt_qc_output.parquet"),
    }
    compare = config.get_target_file_names(
        "compare", "nrt_qc_flag_comparison_{target_name}.tsv"
    )
    paths.update({f"compare_{k}": v for k, v in compare.items()})
    return paths


def _cleanup(paths: dict) -> None:
    for path in paths.values():
        if os.path.exists(path):
            os.remove(path)


class TestRunNRTQC:
    """The run_nrt_qc orchestrator."""

    def test_full_run_with_comparison(self, nrtqc_config_001):
        """All four steps write their outputs for the template config."""
        paths = _output_paths(nrtqc_config_001)
        try:
            nq.run_nrt_qc(nrtqc_config_001)

            for kind in ("qc", "output", "compare_temp", "compare_psal"):
                assert os.path.exists(paths[kind]), kind

            output = pl.read_parquet(paths["output"])
            assert output.shape[0] == 3267
            assert {"temp_nrt_flag", "psal_nrt_flag"} <= set(output.columns)
        finally:
            _cleanup(paths)

    def test_run_without_existing_flags_skips_comparison(self, nrtqc_config_001):
        """Without configured flags, step 4 is skipped entirely."""
        for variable in nrtqc_config_001.data["qc_variable_set"]["variables"]:
            variable.pop("flag", None)

        paths = _output_paths(nrtqc_config_001)
        try:
            nq.run_nrt_qc(nrtqc_config_001)

            assert os.path.exists(paths["output"])
            assert not os.path.exists(paths["compare_temp"])
            assert not os.path.exists(paths["compare_psal"])
        finally:
            _cleanup(paths)

    def test_write_output_false_skips_the_qc_file(self, nrtqc_config_001):
        """``qc: { write_output: false }`` drops only the intermediate file."""
        nrtqc_config_001.data["step_param_set"]["steps"]["qc"]["write_output"] = False

        paths = _output_paths(nrtqc_config_001)
        _cleanup(paths)
        try:
            nq.run_nrt_qc(nrtqc_config_001)

            assert not os.path.exists(paths["qc"])
            for kind in ("output", "compare_temp", "compare_psal"):
                assert os.path.exists(paths[kind]), kind
        finally:
            _cleanup(paths)


class TestNRTQCConfigInterface:
    """Template writing and config reading via the public API."""

    def test_template_read_round_trip(self, test_output_dir):
        """write_config_template produces a readable config."""
        yaml_path = str(test_output_dir / "nrt_qc_template.yaml")
        try:
            nq.write_config_template(yaml_path)
            assert os.path.exists(yaml_path)

            config = nq.read_config(yaml_path)
            assert isinstance(config, NRTQCConfig)
            assert config.dataset_name == "nrt_qc_0001"
            assert config.get_target_names() == ["temp", "psal"]
        finally:
            if os.path.exists(yaml_path):
                os.remove(yaml_path)

    def test_public_exports(self):
        assert set(nq.__all__) == {
            "read_config",
            "read_config_template",
            "run_batch",
            "run_nrt_qc",
            "write_config_template",
        }
        for name in nq.__all__:
            assert callable(getattr(nq, name))


def test_verbose_defaults_to_false():
    """Ported from aiqclib's entry-point signature check: existing callers
    see no progress output unless they ask for it."""
    parameter = inspect.signature(nq.run_nrt_qc).parameters.get("verbose")
    assert parameter is not None
    assert parameter.default is False
