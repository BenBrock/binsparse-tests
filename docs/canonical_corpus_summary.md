# Canonical Corpus Summary

This document summarizes the canonical dense-HDF5 fixtures currently committed
in `binsparse-tests`.

The canonical corpus is defined in
[`config/canonical_matrices.json`](/docker-mount/binsparse-tests/config/canonical_matrices.json).
Each fixture starts from a SuiteSparse Matrix Collection Matrix Market source,
is converted into a semantic dense HDF5 representation, and is paired with
committed Binsparse reference files.

The matrix `kind` labels below are taken from the corresponding SuiteSparse
Matrix Collection entries.

## How To Read The Counts

- `logical nnz` means `sum(pattern)` in the canonical HDF5 file.
- `stored nnz` means `number_of_stored_values` in a committed reference
  `.bsp.h5` file.
- For `general` matrices, `logical nnz == stored nnz`.
- For structured matrices such as `symmetric_lower`, `logical nnz` counts the
  fully expanded semantic matrix while `stored nnz` counts only the stored
  triangle.

## How The Canonical HDF5 Files Are Generated

The canonical files are produced by
[`tools/build_canonical_corpus.py`](/docker-mount/binsparse-tests/tools/build_canonical_corpus.py)
using the logic in
[`src/binsparse_tests/canonical.py`](/docker-mount/binsparse-tests/src/binsparse_tests/canonical.py).

Generation rules:

1. Download the Matrix Market archive listed in the manifest and extract the
   declared `.mtx` member.
2. Parse the Matrix Market banner to obtain the source field and source
   symmetry.
3. Expand the Matrix Market entries into semantic coordinates.
   - `symmetric`, `hermitian`, and `skew-symmetric` inputs are expanded into
     both triangles.
   - Duplicate coordinates are summed before dtype selection.
4. Build two dense arrays:
   - `matrix`: the semantic dense matrix with missing entries filled with zero
   - `pattern`: a dense `uint8` occupancy array where `1` marks a logically
     present entry and `0` marks an absent entry
5. Choose the smallest exact dtype for `matrix` after expansion:
   - `pattern` source -> `uint8`
   - `integer` source -> smallest exact signed/unsigned integer dtype
   - `real` source -> `float32` if every semantic value roundtrips exactly,
     otherwise `float64`
   - `complex` source -> `complex64` if both components roundtrip exactly
     through `float32`, otherwise `complex128`
6. Write a compressed HDF5 file with root datasets:
   - `matrix`
   - `pattern`
7. Write root attributes:
   - `canonical_format_version`
   - `name`
   - `source_field`
   - `source_symmetry`
   - `structure`
   - `is_iso`
   - `value_dtype`
   - `pattern_dtype`
   - `source_url`
   - `source_archive_member`
8. Generate committed reference `.bsp.h5` files from the canonical fixture in
   the currently selected parser using `canonical2bsp`.

Current writer choices:

- binary container: HDF5
- dataset compression: gzip level 9
- dataset layout: chunked, with chunk sizes chosen by `h5py`/HDF5
- canonical `pattern` dtype: `uint8`

## Corpus At A Glance

| Matrix | Kind | Shape | Logical nnz | Source field | Source symmetry | Preferred structure | Canonical dtype | Stored nnz in refs | Reference formats |
| --- | --- | ---: | ---: | --- | --- | --- | --- | ---: | --- |
| `HB/bcspwr01` | Power network problem | `39 x 39` | `131` | `pattern` | `symmetric` | `symmetric_lower` | `uint8` | `85` | `CSR`, `CSC` |
| `Pajek/GD99_b` | Undirected multigraph | `64 x 64` | `252` | `integer` | `symmetric` | `symmetric_lower` | `uint8` | `127` | `CSR`, `CSC` |
| `LPnetlib/lpi_itest2` | Linear programming problem | `9 x 13` | `26` | `real` | `general` | `general` | `float32` | `26` | `CSR`, `CSC` |
| `HB/gre_115` | Directed weighted graph | `115 x 115` | `421` | `real` | `general` | `general` | `float64` | `421` | `CSR`, `CSC` |
| `HB/young1c` | Acoustics problem | `841 x 841` | `4089` | `complex` | `general` | `general` | `complex128` | `4089` | `CSR`, `CSC` |
| `Bai/dwg961a` | Electromagnetics problem | `961 x 961` | `3405` | `complex` | `symmetric` | `symmetric_lower` | `complex128` | `2055` | `CSR`, `CSC` |

## Matrix-By-Matrix Details

### `HB/bcspwr01`

- Canonical file:
  [`fixtures/canonical/HB/bcspwr01.canonical.h5`](/docker-mount/binsparse-tests/fixtures/canonical/HB/bcspwr01.canonical.h5)
- Source archive:
  `http://sparse-files.engr.tamu.edu/MM/HB/bcspwr01.tar.gz`
- Archive member: `bcspwr01/bcspwr01.mtx`
- SuiteSparse kind: power network problem
- Shape: `39 x 39`
- Logical nnz: `131`
- Source field / symmetry: `pattern`, `symmetric`
- Preferred Binsparse structure: `symmetric_lower`
- Canonical HDF5 dtypes:
  - `matrix`: `uint8`
  - `pattern`: `uint8`
- Root attrs:
  - `is_iso = 1`
  - `value_dtype = |u1`
  - `pattern_dtype = |u1`
- HDF5 storage:
  - file size: `13,888` bytes
  - `matrix` chunks: `(39, 39)`, gzip level `9`
  - `pattern` chunks: `(39, 39)`, gzip level `9`
- Reference files:
  - [`fixtures/reference/HB/bcspwr01.csr.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/HB/bcspwr01.csr.bsp.h5)
  - [`fixtures/reference/HB/bcspwr01.csc.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/HB/bcspwr01.csc.bsp.h5)
- Reference encoding notes:
  - stored nnz: `85`
  - value type in committed refs: `iso[bint8]`
  - structure in committed refs: `symmetric_lower`
- Notes:
  - This is the corpus entry for structure-only matrices.
  - The canonical dense file stores the fully expanded logical pattern, while
    the reference `.bsp.h5` files store only one triangle plus structure
    metadata.

### `Pajek/GD99_b`

- Canonical file:
  [`fixtures/canonical/Pajek/GD99_b.canonical.h5`](/docker-mount/binsparse-tests/fixtures/canonical/Pajek/GD99_b.canonical.h5)
- Source archive:
  `http://sparse-files.engr.tamu.edu/MM/Pajek/GD99_b.tar.gz`
- Archive member: `GD99_b/GD99_b.mtx`
- SuiteSparse kind: undirected multigraph
- Shape: `64 x 64`
- Logical nnz: `252`
- Source field / symmetry: `integer`, `symmetric`
- Preferred Binsparse structure: `symmetric_lower`
- Canonical HDF5 dtypes:
  - `matrix`: `uint8`
  - `pattern`: `uint8`
- Root attrs:
  - `is_iso = 0`
  - `value_dtype = |u1`
  - `pattern_dtype = |u1`
- HDF5 storage:
  - file size: `13,888` bytes
  - `matrix` chunks: `(64, 64)`, gzip level `9`
  - `pattern` chunks: `(64, 64)`, gzip level `9`
- Reference files:
  - [`fixtures/reference/Pajek/GD99_b.csr.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/Pajek/GD99_b.csr.bsp.h5)
  - [`fixtures/reference/Pajek/GD99_b.csc.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/Pajek/GD99_b.csc.bsp.h5)
- Reference encoding notes:
  - stored nnz: `127`
  - value type in committed refs: `uint8`
  - structure in committed refs: `symmetric_lower`
- Notes:
  - This is the current integer-valued structured matrix.
  - The integer weights fit exactly in `uint8`, so the canonical dense dataset
    and committed references both avoid wider integer types.

### `LPnetlib/lpi_itest2`

- Canonical file:
  [`fixtures/canonical/LPnetlib/lpi_itest2.canonical.h5`](/docker-mount/binsparse-tests/fixtures/canonical/LPnetlib/lpi_itest2.canonical.h5)
- Source archive:
  `http://sparse-files.engr.tamu.edu/MM/LPnetlib/lpi_itest2.tar.gz`
- Archive member: `lpi_itest2/lpi_itest2.mtx`
- SuiteSparse kind: linear programming problem
- Shape: `9 x 13`
- Logical nnz: `26`
- Source field / symmetry: `real`, `general`
- Preferred Binsparse structure: `general`
- Canonical HDF5 dtypes:
  - `matrix`: `float32`
  - `pattern`: `uint8`
- Root attrs:
  - `is_iso = 0`
  - `value_dtype = <f4`
  - `pattern_dtype = |u1`
- HDF5 storage:
  - file size: `13,888` bytes
  - `matrix` chunks: `(9, 13)`, gzip level `9`
  - `pattern` chunks: `(9, 13)`, gzip level `9`
- Reference files:
  - [`fixtures/reference/LPnetlib/lpi_itest2.csr.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/LPnetlib/lpi_itest2.csr.bsp.h5)
  - [`fixtures/reference/LPnetlib/lpi_itest2.csc.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/LPnetlib/lpi_itest2.csc.bsp.h5)
- Reference encoding notes:
  - stored nnz: `26`
  - value type in committed refs: `float32`
  - no structure key is required
- Notes:
  - This is the current exact-`float32` real matrix.
  - It is useful as a small general matrix whose semantic values do not require
    promotion to `float64`.

### `HB/gre_115`

- Canonical file:
  [`fixtures/canonical/HB/gre_115.canonical.h5`](/docker-mount/binsparse-tests/fixtures/canonical/HB/gre_115.canonical.h5)
- Source archive:
  `http://sparse-files.engr.tamu.edu/MM/HB/gre_115.tar.gz`
- Archive member: `gre_115/gre_115.mtx`
- SuiteSparse kind: directed weighted graph
- Shape: `115 x 115`
- Logical nnz: `421`
- Source field / symmetry: `real`, `general`
- Preferred Binsparse structure: `general`
- Canonical HDF5 dtypes:
  - `matrix`: `float64`
  - `pattern`: `uint8`
- Root attrs:
  - `is_iso = 0`
  - `value_dtype = <f8`
  - `pattern_dtype = |u1`
- HDF5 storage:
  - file size: `17,215` bytes
  - `matrix` chunks: `(29, 29)`, gzip level `9`
  - `pattern` chunks: `(58, 115)`, gzip level `9`
- Reference files:
  - [`fixtures/reference/HB/gre_115.csr.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/HB/gre_115.csr.bsp.h5)
  - [`fixtures/reference/HB/gre_115.csc.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/HB/gre_115.csc.bsp.h5)
- Reference encoding notes:
  - stored nnz: `421`
  - value type in committed refs: `float64`
  - no structure key is required
- Notes:
  - This is the current real matrix that forces `float64`.
  - Together with `lpi_itest2`, it provides both exact-`float32` and
    exact-`float64` real coverage.

### `HB/young1c`

- Canonical file:
  [`fixtures/canonical/HB/young1c.canonical.h5`](/docker-mount/binsparse-tests/fixtures/canonical/HB/young1c.canonical.h5)
- Source archive:
  `http://sparse-files.engr.tamu.edu/MM/HB/young1c.tar.gz`
- Archive member: `young1c/young1c.mtx`
- SuiteSparse kind: acoustics problem
- Shape: `841 x 841`
- Logical nnz: `4089`
- Source field / symmetry: `complex`, `general`
- Preferred Binsparse structure: `general`
- Canonical HDF5 dtypes:
  - `matrix`: `complex128`
  - `pattern`: `uint8`
- Root attrs:
  - `is_iso = 0`
  - `value_dtype = <c16`
  - `pattern_dtype = |u1`
- HDF5 storage:
  - file size: `52,807` bytes
  - `matrix` chunks: `(53, 53)`, gzip level `9`
  - `pattern` chunks: `(106, 106)`, gzip level `9`
- Reference files:
  - [`fixtures/reference/HB/young1c.csr.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/HB/young1c.csr.bsp.h5)
  - [`fixtures/reference/HB/young1c.csc.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/HB/young1c.csc.bsp.h5)
- Reference encoding notes:
  - stored nnz: `4089`
  - value type in committed refs: `complex[float64]`
  - no structure key is required
- Notes:
  - This is the current general complex matrix.
  - In the SuiteSparse collection it is treated as unsymmetric because the
    original Harwell/Boeing file contained both triangles, so the canonical
    fixture intentionally preserves a `general` structure instead of inferring a
    triangular symmetric encoding.

### `Bai/dwg961a`

- Canonical file:
  [`fixtures/canonical/Bai/dwg961a.canonical.h5`](/docker-mount/binsparse-tests/fixtures/canonical/Bai/dwg961a.canonical.h5)
- Source archive:
  `http://sparse-files.engr.tamu.edu/MM/Bai/dwg961a.tar.gz`
- Archive member: `dwg961a/dwg961a.mtx`
- SuiteSparse kind: electromagnetics problem
- Shape: `961 x 961`
- Logical nnz: `3405`
- Source field / symmetry: `complex`, `symmetric`
- Preferred Binsparse structure: `symmetric_lower`
- Canonical HDF5 dtypes:
  - `matrix`: `complex128`
  - `pattern`: `uint8`
- Root attrs:
  - `is_iso = 0`
  - `value_dtype = <c16`
  - `pattern_dtype = |u1`
- HDF5 storage:
  - file size: `94,964` bytes
  - `matrix` chunks: `(31, 61)`, gzip level `9`
  - `pattern` chunks: `(121, 121)`, gzip level `9`
- Reference files:
  - [`fixtures/reference/Bai/dwg961a.csr.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/Bai/dwg961a.csr.bsp.h5)
  - [`fixtures/reference/Bai/dwg961a.csc.bsp.h5`](/docker-mount/binsparse-tests/fixtures/reference/Bai/dwg961a.csc.bsp.h5)
- Reference encoding notes:
  - stored nnz: `2055`
  - value type in committed refs: `complex[float64]`
  - structure in committed refs: `symmetric_lower`
- Notes:
  - This is the current structured complex matrix.
  - It covers the interaction of complex values with triangular structure
    metadata.

## Coverage Summary By Value Class

- pattern / structure-only:
  - `HB/bcspwr01`
- integer:
  - `Pajek/GD99_b`
- real, exact `float32`:
  - `LPnetlib/lpi_itest2`
- real, requires `float64`:
  - `HB/gre_115`
- complex, general:
  - `HB/young1c`
- complex, structured symmetric:
  - `Bai/dwg961a`
