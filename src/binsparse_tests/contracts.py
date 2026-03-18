from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MatrixMarketSpec:
    url: str | None = None
    archive_member: str | None = None
    path: str | None = None


@dataclass(frozen=True)
class BinsparseSpec:
    url: str | None = None
    path: str | None = None
    dataset: str | None = None


@dataclass(frozen=True)
class MatrixFixture:
    name: str
    matrix_market: MatrixMarketSpec | None
    binsparse: BinsparseSpec


@dataclass(frozen=True)
class ParserBinaries:
    name: str
    mtx2bsp: Path
    bsp2mtx: Path
    check_equivalence: Path
