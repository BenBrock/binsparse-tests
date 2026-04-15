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
class CanonicalHdf5Spec:
    url: str | None = None
    path: str | None = None


@dataclass(frozen=True)
class MatrixFixture:
    name: str
    matrix_market: MatrixMarketSpec | None
    binsparse: BinsparseSpec


@dataclass(frozen=True)
class CanonicalReferenceSpec:
    format: str
    url: str | None = None
    path: str | None = None
    dataset: str | None = None


@dataclass(frozen=True)
class CanonicalFixture:
    name: str
    suite_sparse: MatrixMarketSpec
    canonical: CanonicalHdf5Spec
    references: tuple[CanonicalReferenceSpec, ...]


@dataclass(frozen=True)
class CanonicalReferenceCase:
    fixture: CanonicalFixture
    reference: CanonicalReferenceSpec

    @property
    def id(self) -> str:
        return f"{self.fixture.name}[{self.reference.format}]"


@dataclass(frozen=True)
class ParserBinaries:
    name: str
    mtx2bsp: Path
    bsp2mtx: Path
    check_equivalence: Path
    check_canonical_equivalence: Path | None = None
    canonical2bsp: Path | None = None
