# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
As this project is still in active development, it does not yet strictly adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `qc: { write_output: false }` in `step_param_sets` skips the intermediate `qc/nrt_qc_flags.parquet`, whose columns the `nrt_qc` output already holds

### Fixed
- Docs: the tutorial said the `qc` file holds only the item flags; it also holds every input column

## [0.1.5] - 2026-11-06
### Added
- Codecov and CodeFactor badges in the README; a failed coverage upload now fails the Code Coverage workflow

### Changed
- README follows `aiqclib`'s layout: QC test table, installation, core concepts, usage, configuration

## [0.1.4] - 2026-11-06
### Changed
- Docs: the NRT QC how-to becomes "Tuning NRT QC Runs", with the sections repeated elsewhere removed and a new `fail_flag` section

## [0.1.3] - 2026-11-05
### Changed
- Require `aiqclib>=0.15.2`, whose QC items treat NaN as missing like null; `ctddump` input, which stores missing values as NaN, no longer gets them flagged 4

### Removed
- Docs: the NaN-to-null conversion step of the `ctddump` tutorial, no longer needed

## [0.1.2] - 2026-11-05
### Added
- Docs: a Getting Started tutorial (overview, installation, `ctddump`, `seastamp`, running NRT QC) and a page per QC item with diagrams drawn by `docs/diagrams/make_qc_diagrams.py`

## [0.1.1] - 2026-11-05
### Changed
- Allow `aiqclib` 0.15 (`aiqclib>=0.14,<0.16`), which removes its own NRT QC copy; tests pass against 0.15.0 and 0.14.0

## [0.1.0] - 2026-11-05
### Added
- NRT QC pipeline (read input, run QC, concat flags, compare flags), its config, schema and template, moved from `aiqclib` 0.13.0; outputs match `aiqclib` 0.14.0 on the test fixture
- Public API: `run_nrt_qc`, `read_config`, `read_config_template`, `write_config_template`, `run_batch` (no `stage`/`mode` arguments; options after the first are keyword-only for the writer and batch)
- `NRTQCConfig` serves its own `nrt_qc_sets` schema and template through the `aiqclib` 0.14 config hooks
- `run_batch` runs the `nrt_qc` phase on the `aiqclib` batch engine
- Batch processing how-to and API reference pages
