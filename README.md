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

## Design Notes

The canonical command directions are:

- `mtx2bsp`: Matrix Market -> Binsparse
- `bsp2mtx`: Binsparse -> Matrix Market

That matters because the original problem statement swapped those two names in
the prose description of the roundtrip sequence.

See [docs/plan.md](/home/ubuntu/binsparse-tests/docs/plan.md) for the
implementation plan.

