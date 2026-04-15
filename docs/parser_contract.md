# Parser Contract

`binsparse-tests` supports two parser contracts.

## Legacy Roundtrip Contract

These binaries are required for the original Matrix Market-based roundtrip
suite:

- `mtx2bsp`
- `bsp2mtx`
- `check_equivalence`

## Canonical Dense-HDF5 Contract

These binaries are used by the canonical dense-fixture suite:

- `check_canonical_equivalence`
  - required for canonical Phase 1
- `canonical2bsp`
  - optional
  - enables canonical Phase 2 generation tests
  - enables `tools/build_canonical_corpus.py` reference generation

## Expectations

- `check_equivalence LEFT RIGHT`
  - exits zero only when the two parser-readable files are semantically
    equivalent
- `check_canonical_equivalence CANONICAL_H5 MATRIX_FILE`
  - exits zero only when the parser-readable sparse file matches the canonical
    dense values and pattern
- `canonical2bsp CANONICAL_H5 OUTPUT.bsp.h5[:DATASET] FORMAT`
  - writes a binsparse HDF5 matrix in the requested format
  - should preserve the preferred structure recorded in the canonical fixture

## Current Phase-2 Expectations

The initial committed reference corpus uses:

- `CSR`
- `CSC`

Future corpus growth will add more formats, but parsers do not need to
implement every format immediately to participate in the canonical test suite.
