# Design documents

Internal design and planning documents for `nrtqclib`. These are **not** part
of the Sphinx/Read the Docs build (that is `docs/source/` only); they are a
durable record of *why* and *how* a feature was built.

## Migration from aiqclib

| File | What it is |
| --- | --- |
| [`NRTQCLIB_plan.md`](NRTQCLIB_plan.md) | Plan for moving the NRT QC pipeline out of `aiqclib` into this package. |

## NRT QC module (built in aiqclib v0.5.0)

| File | What it is |
| --- | --- |
| [`NRTQC_doc.md`](NRTQC_doc.md) | RTQC recommendation reference: the source material the module was based on. |
| [`NRTQC_spec.md`](NRTQC_spec.md) | Module specification: QC items, flag scheme, config layout, outputs. |
| [`NRTQC_plan.md`](NRTQC_plan.md) | The 8-phase implementation plan followed to build the module in `aiqclib`. |
