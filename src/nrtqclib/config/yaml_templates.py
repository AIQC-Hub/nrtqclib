"""NRT QC YAML template, copied unchanged from aiqclib.common.config.yaml_templates."""


def _get_nrtqc_path_info_sets() -> str:
    """
    Retrieves a YAML template string for NRT QC path information sets.

    This template defines the common, input, and concatenation path
    configurations for the NRT QC process.

    :returns: A string containing the YAML template for NRT QC path info sets.
    :rtype: str
    """
    return """
---
path_info_sets:
  - name: nrt_qc_path_1
    common:
      base_path: /path/to/data # EDIT: Root output directory
    input:
      base_path: /path/to/input # EDIT: Directory with input files
      step_folder_name: ""
    concat:
      step_folder_name: nrt_qc # EDIT: Directory with NRT QC results

"""


def _get_nrtqc_variable_sets() -> str:
    """
    Retrieves a YAML template string for NRT QC variable sets.

    This template lists the variables to run QC items on. The ``flag`` entry
    and the pos/neg flag values are optional; they are only used by the flag
    comparison step when the input already carries NRT QC flags.

    :returns: A string containing the YAML template for QC variable sets.
    :rtype: str
    """
    return """
qc_variable_sets:
  - name: qc_variable_set_1
    variables:
      - name: temp
        flag: temp_qc # Optional: existing NRT QC flag column for comparison
        # Values may be written as 4 or as "4"; the flag column itself may be
        # integer or string. Both sides are read as whole numbers.
        pos_flag_values: [ 4, 6, 7 ] # Optional: for agreement metrics
        neg_flag_values: [ 1 ]
      - name: psal
        flag: psal_qc
        pos_flag_values: [ 4, 6, 7 ]
        neg_flag_values: [ 1 ]

"""


def _get_nrtqc_item_sets() -> str:
    """
    Retrieves a YAML template string for NRT QC item sets.

    This template enables QC items by name and shows the built-in default
    parameters, which can be overridden per item. Items also accept an
    optional ``fail_flag`` (3 or 4, default 4) to soften a failing test, and
    an optional ``include_in_final_flag`` (default :obj:`True`) to keep an
    item running while leaving it out of the aggregated NRT flag.
    Region-dependent values (e.g. regional_range) are edited per region,
    with one configuration file prepared for each region.

    :returns: A string containing the YAML template for QC item sets.
    :rtype: str
    """
    return """
qc_item_sets:
  - name: qc_item_set_1
    items:
      - name: impossible_date
      - name: impossible_location
      - name: global_range
        params: { temp: { min: -2.5, max: 40.0 },
                  psal: { min: 2.0, max: 41.0 } }
      - name: regional_range # EDIT: ranges of this file's region (Mediterranean)
        params: { temp: { min: 10.0, max: 40.0 },
                  psal: { min: 2.0, max: 40.0 } }
      - name: pressure_increasing
      - name: spike
        params: { temp: { shallow: 6.0, deep: 2.0 },
                  psal: { shallow: 0.9, deep: 0.3 },
                  depth_threshold: 500 }
      - name: gradient
        params: { temp: { shallow: 9.0, deep: 3.0 },
                  psal: { shallow: 1.5, deep: 0.5 },
                  depth_threshold: 500 }
      - name: digit_rollover
        params: { temp: 10.0, psal: 5.0 }
      - name: stuck_value
        # Add 'include_in_final_flag: false' to any item to keep its flag
        # column while leaving it out of the aggregated {variable}_nrt_flag.
      - name: density_inversion
        params: { threshold: 0.03 }
      - name: temp_to_psal

"""


def _get_nrtqc_step_class_sets() -> str:
    """
    Retrieves a YAML template string for NRT QC step class sets.

    This template maps each step in the NRT QC pipeline (input, qc, concat,
    compare) to its corresponding Python class name.

    :returns: A string containing the YAML template for NRT QC step class sets.
    :rtype: str
    """
    return """
step_class_sets:
  - name: nrt_qc_step_set_1
    steps:
      input: InputDataSetAll
      qc: QCDataSetAll
      concat: ConcatDataSetAll
      compare: CompareFlagsAll

"""


def _get_nrtqc_step_param_sets() -> str:
    """
    Retrieves a YAML template string for NRT QC step parameter sets.

    This template defines optional parameters for each step in the NRT QC
    pipeline (input, qc, concat, compare).

    :returns: A string containing the YAML template for NRT QC step parameter sets.
    :rtype: str
    """
    return """
step_param_sets:
  - name: nrt_qc_param_set_1
    steps:
      input: { sub_steps: { rename_columns: false,
                            filter_rows: false } }
      qc: { }
      concat: { }
      compare: { }

"""


def _get_nrtqc_sets() -> str:
    """
    Retrieves a YAML template string for defining individual NRT QC sets.

    This template specifies configurations for a particular NRT QC run,
    including its folder and input file names, and references to other
    configuration sets (path info, QC variables, QC items, step classes,
    and step parameters).

    :returns: A string containing the YAML template for NRT QC sets.
    :rtype: str
    """
    return """
nrt_qc_sets:
  - name: nrt_qc_0001  # EDIT: Your NRT QC set name
    dataset_folder_name: nrt_qc_0001  # EDIT: Your output folder
    input_file_name: nrt_cora_bo_4.parquet # EDIT: Your input filename
    path_info: nrt_qc_path_1
    qc_variable_set: qc_variable_set_1
    qc_item_set: qc_item_set_1
    step_class_set: nrt_qc_step_set_1
    step_param_set: nrt_qc_param_set_1

"""


def get_config_nrtqc_template() -> str:
    """
    Retrieve a YAML template string for NRT QC configurations.

    This template includes:

    - ``path_info_sets``: specifying common, input, and concatenation paths.
    - ``qc_variable_sets``: the variables to run QC items on, with optional
      existing-flag entries for the comparison step.
    - ``qc_item_sets``: the enabled QC items and their parameters.
    - ``step_class_sets``: referencing classes for each NRT QC step
      (input, qc, concat, compare).
    - ``step_param_sets``: referencing parameters for the NRT QC steps.
    - ``nrt_qc_sets``: referencing specific dataset folders, files, and
      associated configuration sets.

    :returns: A string containing the YAML template.
    :rtype: str
    """
    return (
        _get_nrtqc_path_info_sets()
        + _get_nrtqc_variable_sets()
        + _get_nrtqc_item_sets()
        + _get_nrtqc_step_class_sets()
        + _get_nrtqc_step_param_sets()
        + _get_nrtqc_sets()
    )
