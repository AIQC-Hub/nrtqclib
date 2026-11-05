# CLAUDE.md

`nrtqclib`: near-real-time QC (NRT QC) pipeline for CTD ocean profiles, split out of `aiqclib` (sibling checkout at `../aiqclib`). It **depends on `aiqclib`**: the QC items (`aiqclib/prepare/features/qc_*.py`), feature registry, flag utilities and config/dataset base classes stay there; this repo owns the pipeline, its config, docs and tests. Source in `src/nrtqclib/` (`step1_read_input` to `step4_compare_flags`, `config/`, `loader/`, `interface/`). Design docs (outside the Sphinx build) in `docs/design/`.

## Migration status (delete this section when the port is done)

- Plan: `docs/design/NRTQCLIB_plan.md`. Phases 2 and 3 happen here; Phases 1 and 4 happen in `aiqclib`. Phase 1 is released as `aiqclib` 0.14.0 (PyPI, 2026-11-05). Do not edit `../aiqclib` from this repo; read it for reference only.
- Files were copied **unchanged** from `aiqclib` `develop` @ `4ba0beb` (0.13.0). Imports still say `aiqclib.*`, so the tests currently exercise aiqclib's copy, not this one. First job: rewrite `aiqclib.nrtqc.*`, `aiqclib.interface.nrtqc`, `aiqclib.common.config.nrtqc_config`, `aiqclib.common.loader.nrtqc_*` to `nrtqclib.*` (mapping table in the plan) in `src/` and `tests/` (including `conftest.py`). Shared imports stay `aiqclib.*`.
- `config/yaml_schema.py` and `config/yaml_templates.py` hold only the NRT QC functions. Wire them into `NRTQCConfig` by overriding the `ConfigBase` class methods `get_yaml_schema(section_name)` (return the schema for `"nrt_qc_sets"`) and `get_template_text(template_name)` (return the template for `"template:nrt_qc_sets"`), deferring to `super()` for anything else.
- Batch: build a `Phase("nrt_qc", "nrt_qc_set_name", "nrt_qc_config", run_nrt_qc, in_all=False, config_reader=nrtqclib.read_config)` and have `nrtqclib.run_batch` call `aiqclib.interface.batch.run_phases((phase,), mode="nrt_qc", config_files={"nrt_qc_config": ...}, table=..., names=..., verbose=..., continue_on_error=...)`. `config_reader` is called as `reader(file)` or `reader(file, set_name=...)`; without it the engine uses `aiqclib.read_config`, which would load aiqclib's deprecated `NRTQCConfig`.
- The `aiqclib` names this package may import are listed in `CONTRACT` in aiqclib `tests/test_common_public_api.py`. Importing a name not listed there needs a matching addition in `aiqclib` first.
- aiqclib 0.14.0 emits a `DeprecationWarning` from its own NRT QC copy (`run_nrt_qc`, `NRTQCConfig`, `read_config` on `nrt_qc_sets`, `run_batch(mode="nrt_qc")`). Seeing one in tests here means an import still points at `aiqclib`.
- Still to port: `test_summary_lists_qc_items` (aiqclib `tests/test_common_base_config.py`), the `nrt_qc` cases in aiqclib `tests/test_interface_config.py`, `tests/test_interface_batch.py` and `tests/test_common_utils_progress.py`, `read_config` / `read_config_template` / `write_config_template` and `run_batch` (the `nrt_qc` batch phase, see the batch bullet above) for this package, the `nrt_qc` section of aiqclib `docs/source/how-to/batch_processing.rst`, `docs/source/api/` (regenerate).
- `pyproject.toml` takes `aiqclib` from `../aiqclib` (editable, `[tool.uv.sources]`). 0.14.0 is on PyPI, so it can switch to the pin `aiqclib>=0.14,<0.15` (drop the `[tool.uv.sources]` entry, `uv sync`); it must before release, since CI's `uv sync --locked` cannot see `../aiqclib`.

## Environment

- Use **`uv`**: `uv sync` installs everything, `uv run <cmd>` runs in the env. No separate install step.
- Shell commands go through **RTK** (global hook, see `~/.claude/RTK.md`) to cut output tokens. Keep output small: run single test files or `-k` selections with `-q`, read file ranges instead of whole files.

## Tests

- `uv run pytest` (small suite). Fixtures are committed: `tests/data/input/nrt_cora_bo_test.parquet`, `tests/data/config/test_dataset_invalid.yaml`. Test outputs go to `tests/data/test/` (gitignored).

## Lint & format

- `uv run ruff format src tests` then `uv run ruff check src tests`. Always run both before merging a feature branch.

## Writing style

- **Never use em or en dashes** anywhere (docs, README, CHANGELOG, docstrings, comments, commit messages). Use a colon, comma, semicolon, parentheses or two sentences; plain hyphen for ranges and minus signs.
- Do not write `--` / `---` in `.rst` as a substitute: `docs/source/conf.py` sets `smartquotes_action = "qe"`; keep it.
- Check: `git ls-files -z | xargs -0 grep -lP '[\x{2013}\x{2014}]'` must print nothing.

## Git (gitflow)

- `main` (releases), `develop` (integration), plus `feature/*`, `release/*`, `hotfix/*`.
- Branch off `develop` for features, off `main` for hotfixes. Do **not** commit directly to `main` or `develop` (the initial import commit is the only exception).

## Releasing

- Checklist in `RELEASING.md`. Order: check the `aiqclib` pin, ruff (+ `sphinx-apidoc` if needed), `CHANGELOG.md`, bump `version` in `pyproject.toml`, `uv sync` (updates `uv.lock`), GitHub release triggers PyPI publish.
- Keep `CHANGELOG.md` **compact**: terse one-line bullets under `### Added/Changed/Fixed/Removed` in `## [Unreleased]` (Keep a Changelog).
- A fix to a QC item ships in `aiqclib` first; this package then raises its `aiqclib` lower bound if it needs the fix.
