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
- Roundtrip test orchestration for both entry points:
  - Matrix Market -> Binsparse -> Matrix Market
  - Binsparse -> Matrix Market -> Binsparse

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

## Run

```bash
pytest -q \
  --parser-config config/parsers.local.json \
  --parser reference-c
```

By default, fixture downloads are cached under `.pytest_cache/binsparse-tests`.

## Finch Adapter

There is also a local Finch adapter under
[tools/finch](/home/ubuntu/binsparse-tests/tools/finch). It exposes the
required `mtx2bsp`, `bsp2mtx`, and `check_equivalence` binaries expected by the
harness.

This adapter currently works around several upstream Finch gaps:

- Finch's normal `.mtx` path rejects symmetric Matrix Market files because it
  routes through `TensorMarket.jl`.
- Finch's current `.bsp.h5` reader does not handle `iso[...]` value encoding.
- Finch's current `.bsp.h5` reader does not handle binsparse `structure`
  metadata such as `symmetric_lower`.

The local adapter uses Julia packages plus Finch's project environment to
provide a working parser target for the current test fixtures.

## Design Notes

The canonical command directions are:

- `mtx2bsp`: Matrix Market -> Binsparse
- `bsp2mtx`: Binsparse -> Matrix Market

That matters because the original problem statement swapped those two names in
the prose description of the roundtrip sequence.

See [docs/plan.md](/home/ubuntu/binsparse-tests/docs/plan.md) for the
implementation plan.
