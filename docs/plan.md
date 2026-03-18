# Implementation Plan

## Goals

Provide a reusable test harness that can validate any Binsparse parser exposing
the following binaries:

- `mtx2bsp`
- `bsp2mtx`
- `check_equivalence`

## Test Contract

For each matrix fixture, run two independent roundtrips.

### 1. Start from Matrix Market

1. `mtx2bsp source.mtx generated.bsp.h5`
2. `check_equivalence source.mtx generated.bsp.h5`
3. `bsp2mtx generated.bsp.h5 regenerated.mtx`
4. `check_equivalence source.mtx regenerated.mtx`

### 2. Start from reference Binsparse

1. `bsp2mtx source.bsp.h5 generated.mtx`
2. `check_equivalence source.bsp.h5 generated.mtx`
3. `mtx2bsp generated.mtx regenerated.bsp.h5`
4. `check_equivalence source.bsp.h5 regenerated.bsp.h5`

## Why pytest

`pytest` is the right default for this repository because it gives us:

- parametrized tests from a matrix manifest
- skip behavior when parser binaries are not configured
- good failure output for subprocess-driven tests
- room for later additions like markers, retries, and parallelism

The harness itself should stay mostly stdlib-based so we do not accumulate
unnecessary dependencies.

## Near-Term Roadmap

### Phase 1

- land the manifest and parser config contract
- implement download and extraction helpers
- implement subprocess wrappers with clear error reporting
- implement roundtrip tests for a single parser

### Phase 2

- support multiple parser definitions in one run
- emit per-step logs and retain failing artifacts
- add checks for optional dataset/group addressing inside `.bsp.h5` files

### Phase 3

- add CI once at least one parser can be built in automation
- integrate Finch and other non-reference parsers
- expand matrix coverage beyond the two initial fixtures

## Local Environment Notes

On this machine at planning time, the following were missing:

- `python3`
- `pytest`
- `cmake`
- HDF5 tooling

That means the code scaffold can be written now, but execution and validation
will require dependency installation before the first real test run.

