from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MatrixMarketSpec:
    url: str
    archive_member: str


@dataclass(frozen=True)
class BinsparseSpec:
    url: str
    dataset: str | None = None


@dataclass(frozen=True)
class MatrixFixture:
    name: str
    matrix_market: MatrixMarketSpec
    binsparse: BinsparseSpec


@dataclass(frozen=True)
class ParserBinaries:
    name: str
    mtx2bsp: Path
    bsp2mtx: Path
    check_equivalence: Path

