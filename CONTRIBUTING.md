# Contributing & Development

For the release process, see [RELEASING.md](RELEASING.md).

## Environment setup

We use **uv** for the development environment. Install it with
`mamba install -n base -c conda-forge uv`, `pip install uv`, or the
[standalone installer](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync    # creates .venv and installs nrtqclib (editable) with all dependencies
```

During the migration from `aiqclib`, `pyproject.toml` takes `aiqclib` from a
sibling checkout (`../aiqclib`, editable). Clone it next to this repository
first.

## Running tests

The test fixtures are small and committed under `tests/data/`, so no download
is needed.

```bash
uv run pytest -v
```

## Code style

We use **Ruff** for linting and formatting.

```bash
uv run ruff format src tests
uv run ruff check src tests
```
