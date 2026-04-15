from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


@dataclass(frozen=True)
class CanonicalMatrix:
    name: str
    matrix: np.ndarray
    pattern: np.ndarray
    source_field: str
    source_symmetry: str
    structure: str
    is_iso: bool
    source_url: str | None = None
    source_archive_member: str | None = None


def _parse_banner(path: Path) -> tuple[str, str]:
    with path.open() as handle:
        banner = handle.readline().strip().split()
    if len(banner) != 5 or banner[0] != "%%MatrixMarket" or banner[1] != "matrix":
        raise ValueError(f"{path} is not a Matrix Market file")
    storage = banner[2].lower()
    if storage != "coordinate":
        raise NotImplementedError(f"unsupported Matrix Market storage: {storage}")
    return banner[3].lower(), banner[4].lower()


def _load_entries(path: Path, field_name: str) -> tuple[int, int, list[tuple[int, int, object]]]:
    with path.open() as handle:
        handle.readline()
        while True:
            line = handle.readline()
            if not line:
                raise ValueError("unexpected end of Matrix Market file")
            if not line.startswith("%"):
                break

        nrows, ncols, nnz = (int(part) for part in line.split())
        entries: list[tuple[int, int, object]] = []
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            row = int(parts[0]) - 1
            col = int(parts[1]) - 1
            if field_name == "pattern":
                value: object = True
            elif field_name == "integer":
                value = int(parts[2])
            elif field_name == "real":
                value = float(parts[2])
            elif field_name == "complex":
                value = complex(float(parts[2]), float(parts[3]))
            else:
                raise NotImplementedError(f"unsupported Matrix Market field: {field_name}")
            entries.append((row, col, value))

    if len(entries) != nnz:
        raise ValueError(f"Matrix Market header declared {nnz} entries, found {len(entries)}")

    return nrows, ncols, entries


def _infer_structure(symmetry: str, entries: list[tuple[int, int, object]]) -> str:
    if symmetry == "general":
        return "general"
    if symmetry == "symmetric":
        base = "symmetric"
    elif symmetry == "hermitian":
        base = "hermitian"
    elif symmetry == "skew-symmetric":
        base = "skew_symmetric"
    else:
        raise NotImplementedError(f"unsupported Matrix Market symmetry: {symmetry}")

    lower = all(row >= col for row, col, _ in entries)
    upper = all(row <= col for row, col, _ in entries)
    if lower and not upper:
        return f"{base}_lower"
    if upper and not lower:
        return f"{base}_upper"
    if lower and upper:
        return f"{base}_lower"
    raise ValueError(f"Matrix Market {symmetry} matrix must store a single triangle")


def _matrix_dtype(values: list[object], field_name: str) -> np.dtype:
    if field_name == "pattern":
        return np.dtype("uint8")
    if field_name == "integer":
        if not values:
            return np.dtype("uint8")
        as_int = [int(value) for value in values]
        min_value = min(as_int)
        max_value = max(as_int)
        if min_value >= 0:
            return np.dtype(np.min_scalar_type(max_value))
        return np.dtype(
            np.promote_types(np.min_scalar_type(min_value), np.min_scalar_type(max_value))
        )
    if field_name == "real":
        if not values:
            return np.dtype("float32")
        data = np.asarray(values, dtype=np.float64)
        if np.array_equal(data.astype(np.float32).astype(np.float64), data):
            return np.dtype("float32")
        return np.dtype("float64")
    if field_name == "complex":
        if not values:
            return np.dtype("complex64")
        data = np.asarray(values, dtype=np.complex128)
        if np.array_equal(data.real.astype(np.float32).astype(np.float64), data.real) and np.array_equal(
            data.imag.astype(np.float32).astype(np.float64), data.imag
        ):
            return np.dtype("complex64")
        return np.dtype("complex128")
    raise NotImplementedError(f"unsupported Matrix Market field: {field_name}")


def _zero_value(field_name: str, dtype: np.dtype):
    if field_name == "complex":
        return np.asarray(0.0 + 0.0j, dtype=dtype)[()]
    return np.asarray(0, dtype=dtype)[()]


def _expand_entry(
    values: dict[tuple[int, int], object],
    pattern_coords: set[tuple[int, int]],
    row: int,
    col: int,
    value: object,
    *,
    structure: str,
    field_name: str,
) -> None:
    def add(r: int, c: int, current_value: object) -> None:
        if field_name == "pattern":
            values[(r, c)] = 1
        else:
            values[(r, c)] = values.get((r, c), 0) + current_value
        pattern_coords.add((r, c))

    add(row, col, value)
    if structure == "general" or row == col:
        return
    if structure.startswith("symmetric_"):
        add(col, row, value)
        return
    if structure.startswith("hermitian_"):
        add(col, row, np.conjugate(value))
        return
    if structure.startswith("skew_symmetric_"):
        add(col, row, -value)
        return
    raise NotImplementedError(f"unsupported structure: {structure}")


def matrix_market_to_canonical(
    path: str | Path,
    *,
    name: str,
    source_url: str | None = None,
    source_archive_member: str | None = None,
) -> CanonicalMatrix:
    source_path = Path(path)
    field_name, symmetry = _parse_banner(source_path)
    nrows, ncols, entries = _load_entries(source_path, field_name)
    structure = _infer_structure(symmetry, entries)
    values: dict[tuple[int, int], object] = {}
    pattern_coords: set[tuple[int, int]] = set()

    for row, col, value in entries:
        _expand_entry(
            values,
            pattern_coords,
            row,
            col,
            value,
            structure=structure,
            field_name=field_name,
        )

    dtype = _matrix_dtype(list(values.values()), field_name)
    matrix = np.full((nrows, ncols), _zero_value(field_name, dtype), dtype=dtype)
    pattern = np.zeros((nrows, ncols), dtype=np.uint8)
    for (row, col), value in values.items():
        matrix[row, col] = value
    for row, col in pattern_coords:
        pattern[row, col] = 1

    return CanonicalMatrix(
        name=name,
        matrix=matrix,
        pattern=pattern,
        source_field=field_name,
        source_symmetry=symmetry,
        structure=structure,
        is_iso=field_name == "pattern",
        source_url=source_url,
        source_archive_member=source_archive_member,
    )


def write_canonical_hdf5(
    path: str | Path,
    canonical: CanonicalMatrix,
    *,
    compression_level: int = 9,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dataset_kwargs: dict[str, object] = {}
    if compression_level > 0:
        dataset_kwargs = {"compression": "gzip", "compression_opts": compression_level}

    with h5py.File(destination, "w") as handle:
        handle.create_dataset("matrix", data=canonical.matrix, **dataset_kwargs)
        handle.create_dataset("pattern", data=canonical.pattern, **dataset_kwargs)
        handle.attrs["canonical_format_version"] = "1"
        handle.attrs["name"] = canonical.name
        handle.attrs["source_field"] = canonical.source_field
        handle.attrs["source_symmetry"] = canonical.source_symmetry
        handle.attrs["structure"] = canonical.structure
        handle.attrs["is_iso"] = int(canonical.is_iso)
        handle.attrs["value_dtype"] = canonical.matrix.dtype.str
        handle.attrs["pattern_dtype"] = canonical.pattern.dtype.str
        if canonical.source_url is not None:
            handle.attrs["source_url"] = canonical.source_url
        if canonical.source_archive_member is not None:
            handle.attrs["source_archive_member"] = canonical.source_archive_member
