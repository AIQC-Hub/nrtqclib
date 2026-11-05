# Releasing (for Maintainers)

For development setup, tests and linting, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Release checklist

Follow these steps in order. Steps marked *if necessary* only apply when the
relevant code has changed since the last release.

1. **Check the `aiqclib` dependency.** `pyproject.toml` must pin a released
   `aiqclib` range (for example `aiqclib>=0.15.2,<0.16`), and the development-only
   `[tool.uv.sources]` path entry must be removed. Widen the upper bound only
   after the tests pass against the new `aiqclib` minor version.
2. **Lint and format** *(if necessary)*:
   ```bash
   uv run ruff format src tests
   uv run ruff check src tests
   ```
3. **Update API documentation** *(if necessary)*: see
   [Building docs locally](#building-docs-locally).
4. **Update `CHANGELOG.md`**: record the changes for the new version.
5. **Bump the version** in `pyproject.toml`, then run `uv sync` so `uv.lock`
   records it.
6. **Commit, then create the release**: once merged into `main`, creating a
   GitHub release triggers the PyPI publish.

## Building docs locally

```bash
uv run sphinx-apidoc -f --remove-old --module-first -o docs/source/api src/nrtqclib
cd docs; uv run make html; cd ..
```

Open `docs/build/html/index.html` to view the site.

## Deployment

The package is published to PyPI by `.github/workflows/publish_to_pypi.yml`
whenever a GitHub release is created. The PyPI project needs a trusted
publisher configured for this repository and the `pypi` environment.
