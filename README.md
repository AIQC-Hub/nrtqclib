# nrtqclib

Near-real-time quality control (NRT QC) for CTD ocean profiles. `nrtqclib`
applies automated real-time QC tests (Argo/CTD RTQC tests) to temperature and
salinity profiles, producing per-item flag columns and a final NRT flag per
variable, and can compare those flags with existing ones.

The QC items are implemented in [`aiqclib`](https://github.com/AIQC-Hub/aiqclib),
which this package depends on. The same tests are available there as training
features for its machine-learning models.

> **Status:** moved out of `aiqclib` (where it shipped as
> `aiqclib.run_nrt_qc` from v0.5.0). See
> [`docs/design/NRTQCLIB_plan.md`](docs/design/NRTQCLIB_plan.md). Not yet on
> PyPI.

## Usage

```python
import nrtqclib as nq

nq.write_config_template("nrt_qc_config.yaml")
# Edit the paths, variables and QC items, then:
config = nq.read_config("nrt_qc_config.yaml")
nq.run_nrt_qc(config)

# Or over a table of datasets (column `nrt_qc_set_name`):
summary = nq.run_batch("datasets.txt", nrt_qc_config="nrt_qc_config.yaml")
```

Migrating from `aiqclib`: the functions keep their names and arguments,
minus `stage` (config functions) and `mode` (`run_batch`). The pipeline,
configuration format and outputs are unchanged.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) and [RELEASING.md](RELEASING.md).

## License

MIT
