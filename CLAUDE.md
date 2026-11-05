# CLAUDE.md

`nrtqclib`: near-real-time QC (NRT QC) pipeline for CTD ocean profiles, split out of `aiqclib` (sibling checkout at `../aiqclib`). It **depends on `aiqclib`**: the QC items (`aiqclib/prepare/features/qc_*.py`), feature registry, flag utilities and config/dataset base classes stay there; this repo owns the pipeline, its config, docs and tests. Source in `src/nrtqclib/` (`step1_read_input` to `step4_compare_flags`, `config/`, `loader/`, `interface/`). Design docs (outside the Sphinx build) in `docs/design/`.

## Migration status (delete this section when the port is done)

- Plan: `docs/design/NRTQCLIB_plan.md`. Phases 2 and 3 happen here; Phases 1 and 4 happen in `aiqclib`. Phase 1 is released as `aiqclib` 0.14.0 (PyPI, 2026-11-05). Do not edit `../aiqclib` from this repo; read it for reference only.
- Done on `feature/move-nrtqc`: imports rewritten to `nrtqclib.*`; `NRTQCConfig` overrides `get_yaml_schema` / `get_template_text`; `nrtqclib.read_config`, `read_config_template`, `write_config_template` (`interface/config.py`) and `run_batch` (`interface/batch.py`, `NRT_QC_PHASE` on `aiqclib.interface.batch.run_phases`); the remaining aiqclib NRT QC tests ported; `how-to/batch_processing.rst`; `docs/source/api/` generated. Parity with `aiqclib.run_nrt_qc` 0.14.0 verified (identical step 2, 3, 4 outputs on the fixture).
- `pytest.ini` turns aiqclib's "is moving to the nrtqclib package" `DeprecationWarning` into an error, so an import pointing back at aiqclib's copy fails the suite.
- The `aiqclib` names this package may import are listed in `CONTRACT` in aiqclib `tests/test_common_public_api.py`. Importing a name not listed there needs a matching addition in `aiqclib` first.
- Remaining: release `nrtqclib` 0.1.0 (Phase 3 step 7), then Phase 4 in `aiqclib`.
- `aiqclib` comes from PyPI (`aiqclib>=0.14,<0.15`). Do not add a `[tool.uv.sources]` path to `../aiqclib`: CI's `uv sync --locked` cannot see it. To test against unreleased aiqclib code, use `uv run --with-editable ../aiqclib pytest` for that run only.

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
