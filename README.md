# nrtqclib

[![PyPI - Version](https://img.shields.io/pypi/v/nrtqclib)](https://pypi.org/project/nrtqclib/)
[![Check Package](https://github.com/AIQC-Hub/nrtqclib/actions/workflows/check_package.yml/badge.svg)](https://github.com/AIQC-Hub/nrtqclib/actions/workflows/check_package.yml)
[![codecov](https://codecov.io/gh/AIQC-Hub/nrtqclib/graph/badge.svg)](https://codecov.io/gh/AIQC-Hub/nrtqclib)
[![CodeFactor](https://www.codefactor.io/repository/github/aiqc-hub/nrtqclib/badge)](https://www.codefactor.io/repository/github/aiqc-hub/nrtqclib)

**nrtqclib** is a Python library that runs **Near-Real Time Quality Control (NRT QC)** on CTD (Conductivity, Temperature, Depth) ocean profiles. It applies the automated real-time QC tests (Argo/CTD RTQC tests) to temperature and salinity, writes one flag column per test and a final NRT flag per variable, and can compare the new flags with the ones already in the data. It is part of the AIQC project, alongside [`aiqclib`](https://github.com/AIQC-Hub/aiqclib), which implements the QC tests and uses their flags as training features for its machine-learning models.

## QC Tests Run by **nrtqclib**

| Item | Test | Level | Catches |
| :--- | :--- | :--- | :--- |
| `impossible_date` | RTQC2 | profile | a timestamp that is missing, too early or in the future |
| `impossible_location` | RTQC3 | profile | a latitude or longitude that is missing or out of bounds |
| `position_on_land` | RTQC4 | profile | a position that is not in the ocean |
| `global_range` | RTQC6 | observation | a value no ocean water can have |
| `regional_range` | RTQC7 | observation | a value outside what the region allows |
| `pressure_increasing` | RTQC8 | observation | pressure that stalls or goes back up the profile |
| `spike` | RTQC9 | observation | a single value sticking out from both neighbours |
| `gradient` | RTQC11 | observation | too steep a change between neighbouring levels |
| `digit_rollover` | RTQC12 | observation | a jump caused by a sensor counter wrapping around |
| `stuck_value` | RTQC13 | profile | a sensor reporting the same value all the way down |
| `density_inversion` | RTQC14 | observation | lighter water under heavier water |
| `temp_to_psal` | rule | observation | salinity computed from a bad temperature |

Flags follow the IOC/Argo scheme: `1` (good), `3` (probably bad) and `4` (bad).

## Installation

The package is available on PyPI and needs Python 3.12 or newer. It installs `aiqclib` as a dependency.

**Using pip:**
```bash
pip install nrtqclib
```

**Using uv:**
```bash
uv pip install nrtqclib
```

`nrtqclib` is not on conda-forge; in a conda environment, install it with `pip`.

## Documentation

Project documentation is hosted on [Read the Docs](https://nrtqclib.readthedocs.io/en/latest/index.html). It includes a Getting Started tutorial that builds the input file with the companion tools [`ctddump`](https://github.com/AIQC-Hub/ctddump) (NetCDF to Parquet) and [`seastamp`](https://github.com/AIQC-Hub/seastamp) (sea floor depth), and a page per QC test.

## Core Concepts

A run reads one Parquet file of CTD observations (one row per observation) and goes through four steps:

1.  **input:** Read and validate the input file.
2.  **qc:** Run every configured QC item, producing one flag column per item and variable.
3.  **concat:** Combine the item flags into the final `temp_nrt_flag` and `psal_nrt_flag` (the most severe item flag) and write the output file.
4.  **compare:** Compare the new flags with the flags already in the input, when the configuration names them.

Each run is controlled by a YAML configuration file, allowing you to define and reproduce your QC runs with ease. Per item, `fail_flag: 3` softens a failure to "probably bad", and `include_in_final_flag: false` keeps the item's column while leaving it out of the final flag.

The QC tests themselves live in `aiqclib`, as `qc_*` features; `nrtqclib` is the pipeline that runs them on their own. It was `aiqclib.run_nrt_qc` up to aiqclib 0.14.0.

## Usage

The workflow follows the same steps as in `aiqclib`:

1.  **Generate a Configuration Template:** Create a starter YAML file.
2.  **Customize the Configuration:** Edit the YAML file to specify paths, the input file and the regional ranges.
3.  **Run NRT QC:** Load the configuration and run the pipeline.

**Step 1: Generate a configuration template.**

```python
import nrtqclib as nq

nq.write_config_template("/path/to/nrt_qc_config.yaml")
```

**Step 2: Customize `nrt_qc_config.yaml`.**
You must edit the file to set the correct input/output paths, the input file name and the regional ranges. See the [Configuration](#configuration) section for details.

**Step 3: Run NRT QC.**
```python
import nrtqclib as nq

config = nq.read_config("/path/to/nrt_qc_config.yaml")
nq.run_nrt_qc(config)
```

This generates the following output folders:
- **qc**: The flag columns of every QC item.
- **nrt_qc**: The input data with the item flags and the final NRT flags.
- **compare**: One report per variable comparing the existing and new flags (contingency table, agreement metrics, per-item breakdown).

### Running several datasets at once

`run_batch` runs NRT QC over a table of datasets (column `nrt_qc_set_name`), returning a summary of every run:

```python
import nrtqclib as nq

summary = nq.run_batch(
    "datasets.txt",                         # table of set names per dataset
    nrt_qc_config="nrt_qc_config.yaml",
    verbose=True,
)
```

See the batch guide in the documentation for the table format and options.

### Migrating from `aiqclib`

`aq.run_nrt_qc`, `aq.read_config`, `aq.read_config_template` and `aq.write_config_template` become `nq.run_nrt_qc`, `nq.read_config`, `nq.read_config_template` and `nq.write_config_template` with the same arguments, minus `stage`; `aq.run_batch(..., mode="nrt_qc")` becomes `nq.run_batch(...)` without `mode`. The pipeline, configuration format and outputs are unchanged.

## Configuration

Configuration is managed via a YAML file. The `write_config_template` function provides a starting point that you must customize.

To inspect the defaults without writing a file, `read_config_template` returns the configuration object instead:

```python
print(nq.read_config_template())
```

The configuration requires you to modify these sections:

- **`path_info_sets`**: Defines the location of input and output data.
  ```yaml
  path_info_sets:
    - name: nrt_qc_path_1
      common:
        base_path: /path/to/data # EDIT: Root output directory
      input:
        base_path: /path/to/input # EDIT: Directory with input files
        step_folder_name: ""
      concat:
        step_folder_name: nrt_qc # EDIT: Directory with NRT QC results
  ```

- **`nrt_qc_sets`**: Defines a specific dataset to be checked.
  ```yaml
  nrt_qc_sets:
    - name: nrt_qc_0001  # EDIT: Your NRT QC set name
      dataset_folder_name: nrt_qc_0001  # EDIT: Your output folder
      input_file_name: nrt_cora_bo_4.parquet # EDIT: Your input filename
  ```

- **`qc_item_sets`**: Lists the QC items and their parameters. The regional range test has no defaults: replace the template's example ranges (Mediterranean) with the ranges of your region.
  ```yaml
  qc_item_sets:
    - name: qc_item_set_1
      items:
        - name: regional_range # EDIT: ranges of this file's region
          params: { temp: { min: 10.0, max: 40.0 },
                    psal: { min: 2.0, max: 40.0 } }
  ```

- **`qc_variable_sets`** *(optional)*: Names the existing flag column of each variable, to compare against.
  ```yaml
  qc_variable_sets:
    - name: qc_variable_set_1
      variables:
        - name: temp
          flag: temp_qc # Optional: existing NRT QC flag column for comparison
          pos_flag_values: [ 4, 6, 7 ] # Optional: for agreement metrics
          neg_flag_values: [ 1 ]
  ```

## Contributing & Development

We welcome contributions! Development setup (uv environment), running tests, and code style are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## Releasing & Deployment (for Maintainers)

The release process (versioning checklist), building the docs, and deployment to PyPI are documented in [RELEASING.md](RELEASING.md).

## License

MIT
