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

## Docs

- [docs/canonical_hdf5.md](/docker-mount/binsparse-tests/docs/canonical_hdf5.md)
  defines the canonical dense-HDF5 fixture contract.
- [docs/canonical_corpus_summary.md](/docker-mount/binsparse-tests/docs/canonical_corpus_summary.md)
  summarizes the currently committed canonical matrices and reference files.
- [docs/parser_contract.md](/docker-mount/binsparse-tests/docs/parser_contract.md)
  defines the parser binary contract.
- [docs/corpus_maintenance.md](/docker-mount/binsparse-tests/docs/corpus_maintenance.md)
  describes corpus selection and regeneration.
- [docs/spec_feature_coverage_checklist.md](/docker-mount/binsparse-tests/docs/spec_feature_coverage_checklist.md)
  tracks which Binsparse features the current committed corpus does and does not cover.
- [docs/plan.md](/docker-mount/binsparse-tests/docs/plan.md)
  records the original legacy roundtrip plan.

## Install

This repository expects Python 3.11+.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Configure A Parser

Create `config/parsers.local.json` from the example file.

The parser contract is documented in
[docs/parser_contract.md](/docker-mount/binsparse-tests/docs/parser_contract.md).

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

Canonical fixtures live in
[config/canonical_matrices.json](/docker-mount/binsparse-tests/config/canonical_matrices.json).

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

## Notes

The canonical command directions are:

- `mtx2bsp`: Matrix Market -> Binsparse
- `bsp2mtx`: Binsparse -> Matrix Market

That matters because the original problem statement swapped those two names in
the prose description of the roundtrip sequence.

The README stays intentionally short. Design and maintenance details belong in
the docs linked above.
