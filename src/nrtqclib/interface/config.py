"""
Reading and writing NRT QC configuration files.

The NRT QC counterparts of ``aiqclib.read_config``, ``read_config_template``
and ``write_config_template``. There is a single stage here, so none of them
takes a ``stage`` argument: they always deal with the ``nrt_qc_sets`` section
and return :class:`~nrtqclib.config.nrtqc_config.NRTQCConfig`.
"""

from typing import Optional

from aiqclib.common.utils.config import get_config_file
from aiqclib.common.utils.config import read_config as utils_read_config
from aiqclib.common.utils.file import ensure_output_file

from nrtqclib.config.nrtqc_config import SECTION_NAME, TEMPLATE_NAME, NRTQCConfig


def write_config_template(
    file_name: str, *, create_dirs: bool = False, overwrite: bool = False
) -> None:
    """
    Write the NRT QC YAML configuration template to a file.

    :param file_name: The path (including filename) where the YAML file will be
                      written. A leading ``~`` is expanded to the user's home
                      directory.
    :type file_name: str
    :param create_dirs: If True, create the output directory (and any missing
                        parents) instead of raising when it does not exist.
                        Defaults to False, so a mistyped path is reported
                        rather than silently creating directories.
    :type create_dirs: bool
    :param overwrite: If True, replace ``file_name`` when it already exists.
                      Defaults to False, so a customized configuration is
                      never silently reset to the template.
    :type overwrite: bool
    :raises IOError: If the directory of ``file_name`` does not exist and
                     ``create_dirs`` is False.
    :raises FileExistsError: If ``file_name`` exists and ``overwrite`` is False.

    Example Usage:
      >>> # write_config_template("~/nrtqc/nrtqc.yaml", create_dirs=True)
    """
    yaml_text = NRTQCConfig.get_template_text(TEMPLATE_NAME)
    file_name = ensure_output_file(
        file_name, create_dirs=create_dirs, overwrite=overwrite
    )

    with open(file_name, "w", encoding="utf-8") as yaml_file:
        yaml_file.write(yaml_text)


def read_config_template(auto_select: bool = True) -> NRTQCConfig:
    """
    Read the bundled NRT QC template as a configuration object.

    The counterpart of :func:`write_config_template`: the same YAML, returned
    as an object instead of written to a file. ``print()`` on the result
    summarizes the QC variables, QC items, steps and output directories.

    .. note::

       The template carries placeholder paths (``/path/to/data``) and a
       placeholder input file name, so the returned object is not ready to
       run with. Set at least ``path_info`` and ``input_file_name`` on it
       first, or write the template out with :func:`write_config_template`,
       edit it, and load it with :func:`read_config`.

    :param auto_select: If True, select the template's single set, so the
                        returned object is fully resolved. Pass False to get
                        the object with nothing selected.
    :type auto_select: bool
    :return: The configuration object.
    :rtype: NRTQCConfig

    Example Usage:
      >>> config = read_config_template()
      >>> config.dataset_name
      'nrt_qc_0001'
    """
    return NRTQCConfig(TEMPLATE_NAME, auto_select)


def read_config(
    file_name: str, set_name: Optional[str] = None, auto_select: bool = True
) -> NRTQCConfig:
    """
    Read an NRT QC YAML configuration file.

    :param file_name: The path (including filename) to the YAML file. Resolved
                      with :func:`aiqclib.common.utils.config.get_config_file`.
    :type file_name: str
    :param set_name: The name of the set to select from the file's
                     ``nrt_qc_sets`` section. Defaults to None.
    :type set_name: Optional[str]
    :param auto_select: If True and no ``set_name`` is given, select the
                        file's only set automatically; a file holding several
                        sets raises, since there is nothing to choose between
                        them. Ignored when ``set_name`` is given. Defaults to
                        True.
    :type auto_select: bool
    :raises ValueError: If the file has no ``nrt_qc_sets`` section (for
                        example an ``aiqclib`` prepare, train or classify
                        configuration).
    :return: The configuration object, with the set selected when
             ``set_name`` is given or ``auto_select`` applies.
    :rtype: NRTQCConfig
    """
    config_file_name = get_config_file(file_name)
    if SECTION_NAME not in utils_read_config(config_file_name):
        raise ValueError(
            f"No '{SECTION_NAME}' section found in {config_file_name}. "
            "Prepare, train and classify configurations are read with "
            "aiqclib.read_config."
        )

    # Auto-selection rejects a file holding several sets, which is exactly
    # the file a caller passing 'set_name' is selecting from.
    config = NRTQCConfig(config_file_name, auto_select and set_name is None)

    if set_name is not None:
        config.select(set_name)

    return config
