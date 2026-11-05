"""JSON schema (as YAML text) for the ``nrt_qc_sets`` configuration section."""


def get_nrtqc_config_schema() -> str:
    """
    Retrieve the YAML-based JSON schema for NRT QC configurations.

    The schema requires path_info_sets, qc_variable_sets, qc_item_sets,
    step_class_sets, step_param_sets, and nrt_qc_sets. QC variables need
    only a ``name`` (``flag`` and the pos/neg flag values are optional and
    used solely by the flag comparison step), while QC items need a ``name``
    plus optional free-form ``params``, a ``fail_flag`` override, and an
    ``include_in_final_flag`` switch controlling whether the item feeds the
    aggregated ``{variable}_nrt_flag``.

    :return: A YAML string representing the JSON schema for NRT QC configurations.
    :rtype: str
    """
    yaml_schema = """
---
type: object
properties:
  path_info_sets:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
        common:
          type: object
          properties:
            base_path:
              type: string
            step_folder_name:
              type: string
          required:
            - base_path
          additionalProperties: false
        input:
          type: object
          properties:
            base_path:
              type: string
            step_folder_name:
              type: string
          required:
            - base_path
            - step_folder_name
          additionalProperties: false
        qc:
          type: object
          properties:
            base_path:
              type: string
            step_folder_name:
              type: string
          additionalProperties: false
        concat:
          type: object
          properties:
            base_path:
              type: string
            step_folder_name:
              type: string
          additionalProperties: false
        compare:
          type: object
          properties:
            base_path:
              type: string
            step_folder_name:
              type: string
          additionalProperties: false
      required:
        - name
        - common
        - input
      additionalProperties: false

  qc_variable_sets:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
        variables:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              flag:
                type: [string, "null"]
              pos_flag_values:
                type: array
              neg_flag_values:
                type: array
            required:
              - name
            additionalProperties: false
      required:
        - name
        - variables
      additionalProperties: false

  qc_item_sets:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
        items:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              params:
                type: object
              fail_flag:
                type: integer
                enum: [3, 4]
              include_in_final_flag:
                type: boolean
            required:
              - name
            additionalProperties: false
      required:
        - name
        - items
      additionalProperties: false

  step_class_sets:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
        steps:
          type: object
          properties:
            input:
              type: string
            qc:
              type: string
            concat:
              type: string
            compare:
              type: string
          required:
            - input
            - qc
            - concat
            - compare
          additionalProperties: false
      required:
        - name
        - steps
      additionalProperties: false

  step_param_sets:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
        steps:
          type: object
          properties:
            input:
              type: object
              properties:
                sub_steps:
                  type: object
                  properties:
                    rename_columns:
                      type: boolean
                    filter_rows:
                      type: boolean
                    validate_columns:
                      type: boolean
                    create_columns:
                      type: boolean
                  required:
                    - rename_columns
                    - filter_rows
                  additionalProperties: false
                rename_dict:
                  type: object
                filter_method_dict:
                  type: object
                  properties:
                    remove_years:
                      type: array
                    keep_years:
                      type: array
                  additionalProperties: false
                create_column_dict:
                  type: object
                  properties:
                    key_columns:
                      type: array
                    sort_columns:
                      type: array
                    columns:
                      type: array
                  additionalProperties: false
              required:
                - sub_steps
              additionalProperties: false
            qc:
              type: object
            concat:
              type: object
            compare:
              type: object
          required:
            - input
            - qc
            - concat
            - compare
          additionalProperties: false
      required:
        - name
        - steps
      additionalProperties: false

  nrt_qc_sets:
    type: array
    items:
      type: object
      properties:
        name:
          type: string
        dataset_folder_name:
          type: string
        input_file_name:
          type: string
        path_info:
          type: string
        qc_variable_set:
          type: string
        qc_item_set:
          type: string
        step_class_set:
          type: string
        step_param_set:
          type: string
      required:
        - name
        - dataset_folder_name
        - input_file_name
        - path_info
        - qc_variable_set
        - qc_item_set
        - step_class_set
        - step_param_set
      additionalProperties: false

additionalProperties: false
required:
  - path_info_sets
  - qc_variable_sets
  - qc_item_sets
  - step_class_sets
  - step_param_sets
  - nrt_qc_sets
"""
    return yaml_schema
