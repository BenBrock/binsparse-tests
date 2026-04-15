# binsparse-tests

Test harness for validating Binsparse parser implementations against two
fixture families:

- legacy Matrix Market <-> Binsparse roundtrips
- canonical dense HDF5 fixtures plus committed reference `.bsp.h5` files

The framework is intentionally small:

- `pytest` provides collection, parametrization, and reporting.
- Python standard library modules handle downloads, archive extraction,
  temporary files, and subprocess execution.
- `numpy` and `h5py` are used for canonical dense fixture generation.
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
- Canonical dense HDF5 fixtures with:
  - a compressed root dataset `matrix`
  - a compressed root dataset `pattern`
  - root attrs carrying the original Matrix Market field/symmetry and the
    preferred Binsparse structure for reference generation
- Phase 1 canonical tests:
  - canonical HDF5 -> reference `.bsp.h5`
- Phase 2 canonical tests:
  - canonical HDF5 -> generated `.bsp.h5` in a requested format
  - generated `.bsp.h5` -> reference `.bsp.h5`

## Install

This repository expects Python 3.11+.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Configure A Parser

Create `config/parsers.local.json` from the example file and point it at the
legacy roundtrip binaries:

- `mtx2bsp`
- `bsp2mtx`
- `check_equivalence`

Canonical fixtures add one required binary and one optional binary:

- `check_canonical_equivalence`
- `canonical2bsp` (optional, used for Phase 2 generation tests and corpus builds)

Example:

```json
{
  "parsers": [
    {
      "name": "reference-c",
      "binaries": {
        "mtx2bsp": "/abs/path/to/mtx2bsp",
        "bsp2mtx": "/abs/path/to/bsp2mtx",
        "check_equivalence": "/abs/path/to/check_equivalence",
        "check_canonical_equivalence": "/abs/path/to/check_canonical_equivalence",
        "canonical2bsp": "/abs/path/to/canonical2bsp"
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

Canonical fixtures live in `config/canonical_matrices.json`. Each entry names:

- the SuiteSparse Matrix Market source
- the local canonical dense HDF5 file
- one or more committed reference `.bsp.h5` files, typically `CSR` and `CSC`

The canonical HDF5 contract is documented in `docs/canonical_hdf5.md`.

## Run

```bash
pytest -q \
  --parser-config config/parsers.local.json \
  --parser reference-c
```

By default, fixture downloads are cached under `.pytest_cache/binsparse-tests`.

To run only the canonical tests:

```bash
pytest -q \
  --matrix-manifest - \
  --parser-config config/parsers.local.json \
  --parser binsparse-python
```

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

To regenerate the committed canonical/reference corpus:

```bash
PYTHONPATH=src python tools/build_canonical_corpus.py \
  --parser-config config/parsers.local.json \
  --parser binsparse-python
```

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

See `docs/plan.md` for the original roundtrip plan and
`docs/canonical_hdf5.md` for the canonical dense-fixture design.
