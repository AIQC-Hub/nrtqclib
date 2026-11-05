# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
As this project is still in active development, it does not yet strictly adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
