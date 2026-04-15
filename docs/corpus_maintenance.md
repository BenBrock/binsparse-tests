# Corpus Maintenance

## Current Corpus

The canonical fixture manifest is [config/canonical_matrices.json](/docker-mount/binsparse-tests/config/canonical_matrices.json).

The current committed matrix set is:

- `HB/bcspwr01`
- `Pajek/GD99_b`
- `LPnetlib/lpi_itest2`
- `HB/gre_115`
- `HB/young1c`
- `Bai/dwg961a`

The current committed reference formats are:

- `CSR`
- `CSC`

## Selection Rules

New canonical fixtures should stay small enough to keep parser validation
cheap, but broad enough to cover different semantic classes:

- pattern
- integer
- real with exact `float32`
- real requiring `float64`
- complex
- structured matrices such as symmetric or Hermitian

Preference order:

1. small matrices
2. semantically distinctive matrices
3. matrices that exercise spec features not already covered

## Regeneration

Regenerate the canonical and reference corpus with:

```bash
PYTHONPATH=src python tools/build_canonical_corpus.py \
  --parser-config config/parsers.local.json \
  --parser binsparse-python
```

The generator:

- downloads the SuiteSparse Matrix Market sources declared in the manifest
- writes canonical dense HDF5 fixtures
- optionally writes committed `.bsp.h5` reference files through a configured
  parser's `canonical2bsp` binary

## Review Checklist

When adding a fixture:

- confirm the Matrix Market source is stable and publicly reachable
- record why the matrix expands coverage
- confirm the canonical `matrix` dtype is minimized exactly
- confirm `pattern` preserves explicit stored zeros when present
- regenerate references and run the canonical suite against at least one parser
