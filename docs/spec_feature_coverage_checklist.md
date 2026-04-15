# Binsparse Spec Feature Coverage Checklist

This checklist tracks which parts of the current Binsparse specification are
covered by the committed canonical dense-HDF5 corpus in `binsparse-tests`.

Scope notes:

- This document is about the current committed corpus, not every feature that a
  parser may already support.
- A checked item means at least one committed canonical fixture or its paired
  reference `.bsp.h5` files exercises that feature.
- An unchecked item is a gap in the current corpus and a candidate for future
  fixtures or reference formats.

## Rank And Container Coverage

- [x] Rank-2 matrix coverage
  Current corpus is entirely matrix-shaped.
- [ ] Rank-1 vector coverage (`DVEC`, `CVEC`)
- [ ] Rank-N tensor coverage through custom formats
- [x] HDF5 container coverage
  All committed canonical and reference files are HDF5.
- [ ] NetCDF container coverage
- [ ] Nested HDF5 group-addressed fixture coverage (`file.h5:group`)
  Current committed fixtures live at the root group.

## Predefined Matrix Format Coverage

- [x] `CSR`
  All six matrices have committed `CSR` references.
- [x] `CSC`
  All six matrices have committed `CSC` references.
- [ ] `DCSR`
- [ ] `DCSC`
- [ ] `COOR`
- [ ] `COOC`
- [ ] `COO` alias coverage
- [ ] `DVEC`
- [ ] `DMATR`
- [ ] `DMATC`
- [ ] `DMAT` alias coverage

## Custom Format Coverage

- [ ] `custom` format descriptors
- [ ] `level` hierarchy coverage
- [ ] `transpose` coverage for custom formats
- [ ] equivalent-format alias emission for custom tensor descriptors

## Matrix Structure Coverage

- [x] `general`
  Covered by `LPnetlib/lpi_itest2`, `HB/gre_115`, and `HB/young1c`.
- [x] `symmetric_lower`
  Covered by `HB/bcspwr01`, `Pajek/GD99_b`, and `Bai/dwg961a`.
- [ ] `symmetric_upper`
- [ ] `hermitian_lower`
- [ ] `hermitian_upper`
- [ ] `skew_symmetric_lower`
- [ ] `skew_symmetric_upper`
- [ ] `number_of_diagonal_elements`

## Value Type Coverage In Committed References

- [x] `bint8`
  Covered by `HB/bcspwr01` via `iso[bint8]`.
- [x] `uint8`
  Covered by `Pajek/GD99_b`.
- [ ] `uint16`
- [ ] `uint32`
- [ ] `uint64`
- [ ] `int8`
- [ ] `int16`
- [ ] `int32`
- [ ] `int64`
- [x] `float32`
  Covered by `LPnetlib/lpi_itest2`.
- [x] `float64`
  Covered by `HB/gre_115`.
- [ ] `complex[float32]`
- [x] `complex[float64]`
  Covered by `HB/young1c` and `Bai/dwg961a`.

## Value Modifier Coverage In Committed References

- [x] `iso[...]`
  Covered by `HB/bcspwr01`.
- [x] `complex[...]`
  Covered by `HB/young1c` and `Bai/dwg961a`.

## Index And Pointer Type Coverage In Committed References

- [x] `int32` index / pointer arrays
  All current committed references use `int32` indices and pointers.
- [ ] `uint8` index / pointer arrays
- [ ] `uint16` index / pointer arrays
- [ ] `uint32` index / pointer arrays
- [ ] `uint64` index / pointer arrays
- [ ] `int8` index / pointer arrays
- [ ] `int16` index / pointer arrays
- [ ] `int64` index / pointer arrays

## Semantic Matrix Class Coverage

- [x] pattern / structure-only matrices
  `HB/bcspwr01`
- [x] integer-valued matrices
  `Pajek/GD99_b`
- [x] real matrices exactly representable in `float32`
  `LPnetlib/lpi_itest2`
- [x] real matrices requiring `float64`
  `HB/gre_115`
- [x] complex matrices
  `HB/young1c`, `Bai/dwg961a`
- [x] symmetric matrices
  `HB/bcspwr01`, `Pajek/GD99_b`, `Bai/dwg961a`
- [x] unsymmetric / general matrices
  `LPnetlib/lpi_itest2`, `HB/gre_115`, `HB/young1c`
- [x] rectangular matrices
  `LPnetlib/lpi_itest2`
- [ ] Hermitian matrices
- [ ] skew-symmetric matrices

## Canonical Dense-HDF5 Semantics Coverage

- [x] separate dense `matrix` and dense `pattern` datasets
- [x] zero fill for absent coordinates
- [x] symmetry expansion from Matrix Market source into canonical dense form
- [x] exact dtype minimization after semantic expansion
- [x] preservation of occupancy separate from values
  This is fundamental to every current canonical fixture.
- [ ] explicit stored zeros from source data
  No current committed matrix has an explicit-zero case.
- [ ] duplicate Matrix Market coordinate aggregation
  The generator supports it, but the committed corpus does not currently test it.

## Descriptor / Metadata Coverage

- [x] `format`
- [x] `shape`
- [x] `number_of_stored_values`
- [x] `data_types`
- [x] `structure` where needed
- [x] variable-length UTF-8 JSON descriptor attribute in HDF5 references
- [ ] additional optional metadata beyond the current reference set

## Highest-Value Current Gaps

If the corpus expands next, the highest-value additions are:

- [ ] one Hermitian complex matrix
- [ ] one skew-symmetric matrix
- [ ] one matrix with explicit stored zeros
- [ ] one matrix whose exact complex dtype is `complex[float32]`
- [ ] one signed-integer matrix
- [ ] `DCSR` and `DCSC` reference files
- [ ] `COOR` / `COOC` reference files
- [ ] one vector fixture
- [ ] one tensor/custom-format fixture
