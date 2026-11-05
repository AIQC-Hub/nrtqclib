"""Unit tests for ``nrtqclib.run_batch``.

Ported from the ``nrt_qc`` cases of aiqclib ``tests/test_interface_batch.py``.
The table parsing, skipping and summary logic belong to aiqclib's batch
engine and are tested there; these tests check that the NRT QC phase is wired
to it correctly. The runner and config reader are stubbed, so no YAML file or
input data has to exist.
"""

from dataclasses import replace

import polars as pl
import pytest

from nrtqclib.interface import batch as batch_module
from nrtqclib.interface.batch import run_batch


TABLE_TEXT = """\
name       prepare_set_name       nrt_qc_set_name
ar_ar      dataset_ar_ar_0001     nrt_qc_ar_ar_0001
bo_bo      dataset_bo_bo_0001     nrt_qc_bo_bo_0001
cora_mo    dataset_cora_mo_0001   nrt_qc_cora_mo_0001
"""


@pytest.fixture
def table_file(tmp_path):
    """A whitespace-aligned table shared with aiqclib's prepare phase."""
    path = tmp_path / "datasets.txt"
    path.write_text(TABLE_TEXT, encoding="utf-8")
    return str(path)


@pytest.fixture
def calls(monkeypatch):
    """Stub the phase's reader and runner, returning the call log.

    Each entry is ``(config_file, set_name, verbose)``.
    """
    log = []

    def fake_read_config(file_name, set_name=None, auto_select=True):
        return {"config_file": file_name, "set_name": set_name}

    def recorder(config, verbose=False):
        log.append((config["config_file"], config["set_name"], verbose))

    monkeypatch.setattr(
        batch_module,
        "NRT_QC_PHASE",
        replace(
            batch_module.NRT_QC_PHASE,
            runner=recorder,
            config_reader=fake_read_config,
        ),
    )
    return log


class TestRunBatch:
    def test_one_run_per_dataset(self, table_file, calls):
        summary = run_batch(table_file, nrt_qc_config="nrtqc.yaml")
        assert len(calls) == 3
        assert summary["phase"].to_list() == ["nrt_qc"] * 3
        assert summary["status"].to_list() == ["ok"] * 3

    def test_set_names_come_from_the_nrt_qc_column(self, table_file, calls):
        """Other columns of a shared aiqclib table are ignored."""
        run_batch(table_file, nrt_qc_config="nrtqc.yaml")
        assert [call[1] for call in calls] == [
            "nrt_qc_ar_ar_0001",
            "nrt_qc_bo_bo_0001",
            "nrt_qc_cora_mo_0001",
        ]

    def test_uses_the_nrt_qc_config_file(self, table_file, calls):
        run_batch(table_file, nrt_qc_config="nrtqc.yaml")
        assert {call[0] for call in calls} == {"nrtqc.yaml"}

    def test_names_selects_rows(self, table_file, calls):
        summary = run_batch(table_file, nrt_qc_config="nrtqc.yaml", names=["bo_bo"])
        assert [call[1] for call in calls] == ["nrt_qc_bo_bo_0001"]
        assert summary["name"].to_list() == ["bo_bo"]

    def test_verbose_is_passed_on(self, table_file, calls, capsys):
        run_batch(table_file, nrt_qc_config="nrtqc.yaml", verbose=True)
        assert all(call[2] is True for call in calls)
        assert "nrt_qc" in capsys.readouterr().out

    def test_missing_config_names_the_argument(self, table_file, calls):
        with pytest.raises(ValueError, match="nrt_qc_config"):
            run_batch(table_file)

    def test_missing_column_names_the_column(self, tmp_path, calls):
        path = tmp_path / "datasets.txt"
        path.write_text("name  prepare_set_name\nar_ar  dataset_ar_ar_0001\n")
        with pytest.raises(ValueError, match="nrt_qc_set_name"):
            run_batch(str(path), nrt_qc_config="nrtqc.yaml")

    def test_blank_cell_skips_the_dataset(self, tmp_path, calls):
        """A .tsv, since a whitespace table cannot carry an empty last field."""
        path = tmp_path / "datasets.tsv"
        path.write_text("name\tnrt_qc_set_name\nar_ar\tnrt_qc_ar_ar_0001\nbo_bo\t\n")
        summary = run_batch(str(path), nrt_qc_config="nrtqc.yaml")
        assert [call[1] for call in calls] == ["nrt_qc_ar_ar_0001"]
        assert summary["status"].to_list() == ["ok", "skipped"]

    def test_without_a_table(self, calls):
        """Without a table the config file selects its own set."""
        summary = run_batch(nrt_qc_config="nrtqc.yaml")
        assert calls == [("nrtqc.yaml", None, False)]
        assert summary["status"].to_list() == ["ok"]

    def test_dataframe_table(self, calls):
        table = pl.DataFrame({"name": ["ar_ar"], "nrt_qc_set_name": ["set_a"]})
        run_batch(table, nrt_qc_config="nrtqc.yaml")
        assert [call[1] for call in calls] == ["set_a"]

    def test_failure_is_recorded_with_continue_on_error(self, table_file, monkeypatch):
        def failing(config, verbose=False):
            raise RuntimeError("boom")

        monkeypatch.setattr(
            batch_module,
            "NRT_QC_PHASE",
            replace(
                batch_module.NRT_QC_PHASE,
                runner=failing,
                config_reader=lambda file_name, set_name=None: {},
            ),
        )
        summary = run_batch(
            table_file, nrt_qc_config="nrtqc.yaml", continue_on_error=True
        )
        assert summary["status"].to_list() == ["failed"] * 3
        assert summary["error"].to_list()[0] == "RuntimeError: boom"

    def test_options_are_keyword_only(self, table_file):
        """aiqclib's ``run_batch(table, mode, ...)`` shape fails loudly."""
        with pytest.raises(TypeError):
            run_batch(table_file, "nrt_qc")


class TestPhase:
    """The phase is wired to this package's code, not aiqclib's copy.

    Checked against the unstubbed phase, since the fixtures above replace it.
    """

    def test_runner_is_run_nrt_qc(self):
        from nrtqclib.interface.nrtqc import run_nrt_qc

        assert batch_module.NRT_QC_PHASE.runner is run_nrt_qc

    def test_reader_is_this_packages_read_config(self):
        from nrtqclib.interface.config import read_config

        assert batch_module.NRT_QC_PHASE.config_reader is read_config

    def test_names(self):
        phase = batch_module.NRT_QC_PHASE
        assert phase.name == "nrt_qc"
        assert phase.column == "nrt_qc_set_name"
        assert phase.config_argument == "nrt_qc_config"
        assert phase.in_all is False


def test_end_to_end_without_stubs(tmp_path, input_dir):
    """A real config file and runner, through the engine, from a table."""
    import yaml

    from nrtqclib.config.nrtqc_config import NRTQCConfig

    config = yaml.safe_load(NRTQCConfig.get_template_text("template:nrt_qc_sets"))
    path_info = config["path_info_sets"][0]
    path_info["common"]["base_path"] = str(tmp_path / "out")
    path_info["input"]["base_path"] = str(input_dir)
    config["nrt_qc_sets"][0]["input_file_name"] = "nrt_cora_bo_test.parquet"
    config_path = tmp_path / "nrtqc.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    table = pl.DataFrame({"name": ["bo"], "nrt_qc_set_name": ["nrt_qc_0001"]})
    summary = run_batch(table, nrt_qc_config=str(config_path))

    assert summary["status"].to_list() == ["ok"], summary["error"].to_list()
    assert any((tmp_path / "out").rglob("*.parquet"))
