# Finch Integration Notes

## Status

The repository includes a local Finch adapter in
[tools/finch](/home/ubuntu/binsparse-tests/tools/finch) that passed the current
test matrix set on 2026-03-17.

Validated command:

```bash
/home/ubuntu/binsparse-tests/.venv/bin/pytest -q \
  --parser-config /home/ubuntu/binsparse-tests/config/parsers.local.json \
  --parser finch-local
```

Observed result:

- `4 passed in 136.46s`

## What The Adapter Does

The adapter provides the three expected parser binaries:

- `mtx2bsp`
- `bsp2mtx`
- `check_equivalence`

Implementation approach:

- use `MatrixMarket.jl` to read `.mtx` files semantically
- use direct HDF5+JSON handling for `.bsp.h5` files
- normalize both formats to sparse Julia matrices
- use Finch tensor conversions as part of the adapter path

## Current Upstream Finch Gaps

The local adapter exists because Finch itself is not yet sufficient to serve as
the parser binaries directly for these fixtures.

Observed issues:

- Finch's `.mtx` route uses `TensorMarket.jl`, which rejects at least the
  `symmetric` Matrix Market header used by `chesapeake.mtx`.
- Finch's binsparse reader errors on `iso[...]` value encoding.
- Finch's binsparse reader errors on binsparse `structure` metadata such as
  `symmetric_lower`.
- Finch does not currently ship standalone CLI binaries for this harness.

## Upstream PR Direction

Reasonable upstream work in Finch would be:

- add first-class Matrix Market support for matrix files that preserves
  symmetry-aware headers
- add binsparse reader support for `iso[...]` values
- add binsparse reader support for `structure` metadata
- optionally add small CLI entry points or example scripts for
  `mtx2bsp`, `bsp2mtx`, and `check_equivalence`
