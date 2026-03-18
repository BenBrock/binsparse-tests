# binsparse-tests

Test harness for validating Binsparse parser implementations against paired
Matrix Market and Binsparse fixtures.

The framework is intentionally small:

- `pytest` provides collection, parametrization, and reporting.
- Python standard library modules handle downloads, archive extraction,
  temporary files, and subprocess execution.
- Parser-specific paths live in a local JSON config so the same tests can run
  against multiple implementations.

## Current Scope

The initial scaffold covers:

- A structured manifest of known test matrices in
  [config/matrices.json](/home/ubuntu/binsparse-tests/config/matrices.json).
- A parser config contract in
  [config/parsers.example.json](/home/ubuntu/binsparse-tests/config/parsers.example.json).
- Roundtrip test orchestration for both entry points when both fixture formats
  are available:
  - Matrix Market -> Binsparse -> Matrix Market
  - Binsparse -> Matrix Market -> Binsparse
- Binsparse-only fixture discovery from a local directory tree, which collects
  just the Binsparse -> Matrix Market -> Binsparse roundtrip.

## Install

This repository expects Python 3.11+.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Configure A Parser

Create `config/parsers.local.json` from the example file and point it at the
three required binaries:

- `mtx2bsp`
- `bsp2mtx`
- `check_equivalence`

Example:

```json
{
  "parsers": [
    {
      "name": "reference-c",
      "binaries": {
        "mtx2bsp": "/abs/path/to/mtx2bsp",
        "bsp2mtx": "/abs/path/to/bsp2mtx",
        "check_equivalence": "/abs/path/to/check_equivalence"
      }
    }
  ]
}
```

Fixture manifests may also use local paths. `matrix_market` is optional, so a
fixture can be Binsparse-only:

```json
{
  "matrices": [
    {
      "name": "AG-Monien/3elt",
      "matrix_market": null,
      "binsparse": {
        "path": "/binsparse-data/data/SuiteSparse_coo_noz_primary/AG-Monien/3elt.coo.bsp.h5",
        "dataset": null
      }
    }
  ]
}
```

## Run

```bash
pytest -q \
  --parser-config config/parsers.local.json \
  --parser reference-c
```

By default, fixture downloads are cached under `.pytest_cache/binsparse-tests`.

To run local Binsparse-only fixtures without the default manifest:

```bash
pytest -q \
  --matrix-manifest - \
  --binsparse-root /binsparse-data/data/SuiteSparse_coo_noz_primary \
  --parser-config config/parsers.local.json \
  --parser reference-c
```

With this mode, fixtures discovered under `--binsparse-root` only run the
`bsp2mtx -> mtx2bsp` roundtrip. Fixtures that also define `matrix_market`
continue to run both directions.

For Finch, point `config/parsers.local.json` at the upstream commands in your
local [Finch.jl](/docker-mount/Finch.jl) checkout:

- [mtx2bsp](/docker-mount/Finch.jl/bin/mtx2bsp)
- [bsp2mtx](/docker-mount/Finch.jl/bin/bsp2mtx)
- [check_equivalence](/docker-mount/Finch.jl/bin/check_equivalence)

## Design Notes

The canonical command directions are:

- `mtx2bsp`: Matrix Market -> Binsparse
- `bsp2mtx`: Binsparse -> Matrix Market

That matters because the original problem statement swapped those two names in
the prose description of the roundtrip sequence.

See [docs/plan.md](/home/ubuntu/binsparse-tests/docs/plan.md) for the
implementation plan.
