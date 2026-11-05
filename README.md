# nrtqclib

Near-real-time quality control (NRT QC) for CTD ocean profiles. `nrtqclib`
applies automated real-time QC tests (Argo/CTD RTQC tests) to temperature and
salinity profiles, producing per-item flag columns and a final NRT flag per
variable, and can compare those flags with existing ones.

The QC items are implemented in [`aiqclib`](https://github.com/AIQC-Hub/aiqclib),
which this package depends on. The same tests are available there as training
features for its machine-learning models.

> **Status:** being moved out of `aiqclib` (where it shipped as
> `aiqclib.run_nrt_qc` from v0.5.0). See
> [`docs/design/NRTQCLIB_plan.md`](docs/design/NRTQCLIB_plan.md). Not yet on
> PyPI.

## Usage

```python
import nrtqclib

config = ...  # NRT QC config, see docs/source/configuration/nrtqc.rst
nrtqclib.run_nrt_qc(config)
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) and [RELEASING.md](RELEASING.md).

## License

MIT
