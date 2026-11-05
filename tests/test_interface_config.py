"""Unit tests for the public config interface: ``read_config``,
``read_config_template`` and ``write_config_template``.

Ported from the ``nrt_qc`` cases of aiqclib ``tests/test_interface_config.py``.
There is one stage here, so the functions take no ``stage`` argument.
"""

import pytest
import yaml

from nrtqclib.config.nrtqc_config import NRTQCConfig
from nrtqclib.interface.config import (
    read_config,
    read_config_template,
    write_config_template,
)


@pytest.fixture
def multi_set_yaml(tmp_path):
    """The bundled template with a second NRT QC set, written to a file."""
    config = yaml.safe_load(NRTQCConfig.get_template_text("template:nrt_qc_sets"))
    second = dict(config["nrt_qc_sets"][0], name="nrt_qc_0002")
    config["nrt_qc_sets"].append(second)
    path = tmp_path / "multi.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return str(path)


class TestWriteConfigTemplate:
    """Tests for ``write_config_template``."""

    def test_writes_the_template(self, tmp_path):
        path = tmp_path / "nrtqc.yaml"
        write_config_template(str(path))
        assert path.read_text() == NRTQCConfig.get_template_text("template:nrt_qc_sets")

    def test_existing_file_is_not_replaced_by_default(self, tmp_path):
        path = tmp_path / "nrtqc.yaml"
        path.write_text("keep me")
        with pytest.raises(FileExistsError, match="overwrite=True"):
            write_config_template(str(path))
        assert path.read_text() == "keep me"

    def test_overwrite_replaces_the_file(self, tmp_path):
        path = tmp_path / "nrtqc.yaml"
        path.write_text("replace me")
        write_config_template(str(path), overwrite=True)
        assert "nrt_qc_sets:" in path.read_text()

    def test_missing_directory_message_names_the_option(self, tmp_path):
        path = tmp_path / "missing" / "nrtqc.yaml"
        with pytest.raises(IOError, match="create_dirs=True"):
            write_config_template(str(path))

    def test_create_dirs_creates_missing_directories(self, tmp_path):
        path = tmp_path / "a" / "b" / "nrtqc.yaml"
        write_config_template(str(path), create_dirs=True)
        assert path.exists()

    def test_tilde_path_is_expanded(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        write_config_template("~/config/nrtqc.yaml", create_dirs=True)
        assert (tmp_path / "config" / "nrtqc.yaml").exists()

    def test_options_are_keyword_only(self, tmp_path):
        """aiqclib's ``(file_name, "nrt_qc")`` call shape fails loudly.

        A second positional argument would otherwise land in ``create_dirs``
        and be taken as True.
        """
        with pytest.raises(TypeError):
            write_config_template(str(tmp_path / "nrtqc.yaml"), "nrt_qc")


class TestReadConfigTemplate:
    """Tests for ``read_config_template``."""

    def test_returns_a_resolved_config(self):
        config = read_config_template()
        assert isinstance(config, NRTQCConfig)
        assert config.dataset_name == "nrt_qc_0001"
        assert config.data is not None

    def test_without_auto_select(self):
        config = read_config_template(auto_select=False)
        assert config.data is None
        assert config.dataset_name is None
        assert config.full_config is not None

    def test_matches_the_written_template(self, tmp_path):
        """The object is built from the same YAML the file would contain."""
        path = tmp_path / "template.yaml"
        write_config_template(str(path))
        written = yaml.safe_load(path.read_text())
        assert read_config_template(auto_select=False).full_config == written

    def test_returns_an_independent_object(self):
        """Each call builds a fresh object, so edits do not leak between them."""
        first = read_config_template()
        first.data["path_info"]["common"]["base_path"] = "/somewhere/else"
        second = read_config_template()
        assert second.data["path_info"]["common"]["base_path"] == "/path/to/data"


class TestReadConfig:
    """Tests for ``read_config``."""

    def test_reads_a_single_set_file(self, tmp_path):
        path = tmp_path / "nrtqc.yaml"
        write_config_template(str(path))
        config = read_config(str(path))
        assert isinstance(config, NRTQCConfig)
        assert config.dataset_name == "nrt_qc_0001"
        assert config.get_target_names() == ["temp", "psal"]

    def test_set_name_selects_from_a_multi_set_file(self, multi_set_yaml):
        for name in ("nrt_qc_0001", "nrt_qc_0002"):
            config = read_config(multi_set_yaml, set_name=name)
            assert config.dataset_name == name

    def test_auto_select_false_still_honoured(self, multi_set_yaml):
        config = read_config(multi_set_yaml, "nrt_qc_0002", False)
        assert config.dataset_name == "nrt_qc_0002"

    def test_auto_select_false_without_a_name(self, multi_set_yaml):
        config = read_config(multi_set_yaml, auto_select=False)
        assert config.dataset_name is None

    def test_multi_set_file_without_a_set_name_raises(self, multi_set_yaml):
        with pytest.raises(ValueError, match="multiple data set names"):
            read_config(multi_set_yaml)

    def test_unknown_set_name_raises(self, multi_set_yaml):
        with pytest.raises(ValueError, match="no_such_set"):
            read_config(multi_set_yaml, set_name="no_such_set")

    def test_file_without_the_section_raises(self, config_dir):
        """A non-NRT QC file is rejected with a pointer to aiqclib."""
        with pytest.raises(ValueError, match="aiqclib.read_config"):
            read_config(str(config_dir / "test_dataset_invalid.yaml"))

    def test_invalid_path_raises(self, tmp_path):
        with pytest.raises(IOError):
            read_config(str(tmp_path / "missing.yaml"))
