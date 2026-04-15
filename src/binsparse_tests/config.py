from __future__ import annotations

import json
from pathlib import Path

from .contracts import BinsparseSpec
from .contracts import CanonicalFixture
from .contracts import CanonicalHdf5Spec
from .contracts import CanonicalReferenceSpec
from .contracts import MatrixFixture
from .contracts import MatrixMarketSpec
from .contracts import ParserBinaries


def _resolve_entry_path(base_dir: Path, entry: dict[str, object]) -> dict[str, object]:
    resolved = dict(entry)
    path = resolved.get("path")
    if isinstance(path, str):
        candidate = Path(path)
        if not candidate.is_absolute():
            resolved["path"] = str((base_dir / candidate).resolve())
    return resolved


def load_matrix_manifest(path: Path) -> list[MatrixFixture]:
    payload = json.loads(path.read_text())
    base_dir = path.parent
    fixtures: list[MatrixFixture] = []
    for entry in payload["matrices"]:
        matrix_market = None
        if entry.get("matrix_market") is not None:
            matrix_market = MatrixMarketSpec(
                **_resolve_entry_path(base_dir, entry["matrix_market"])
            )
        fixtures.append(
            MatrixFixture(
                name=entry["name"],
                matrix_market=matrix_market,
                binsparse=BinsparseSpec(**_resolve_entry_path(base_dir, entry["binsparse"])),
            )
        )
    return fixtures


def discover_binsparse_fixtures(root: Path) -> list[MatrixFixture]:
    fixtures: list[MatrixFixture] = []
    for path in sorted(root.rglob("*.bsp.h5")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        fixtures.append(
            MatrixFixture(
                name=_fixture_name_from_binsparse_path(relative_path),
                matrix_market=None,
                binsparse=BinsparseSpec(path=str(path)),
            )
        )
    return fixtures


def load_canonical_manifest(path: Path) -> list[CanonicalFixture]:
    payload = json.loads(path.read_text())
    base_dir = path.parent
    fixtures: list[CanonicalFixture] = []
    for entry in payload["matrices"]:
        fixtures.append(
            CanonicalFixture(
                name=entry["name"],
                suite_sparse=MatrixMarketSpec(
                    **_resolve_entry_path(base_dir, entry["suite_sparse"])
                ),
                canonical=CanonicalHdf5Spec(
                    **_resolve_entry_path(base_dir, entry["canonical"])
                ),
                references=tuple(
                    CanonicalReferenceSpec(
                        **_resolve_entry_path(base_dir, reference)
                    )
                    for reference in entry.get("references", [])
                ),
            )
        )
    return fixtures


def _fixture_name_from_binsparse_path(path: Path) -> str:
    name = path.as_posix()
    for suffix in (".coo.bsp.h5", ".bsp.h5"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return str(path.with_suffix(""))


def load_parser_manifest(path: Path) -> dict[str, ParserBinaries]:
    payload = json.loads(path.read_text())
    parsers: dict[str, ParserBinaries] = {}
    for entry in payload["parsers"]:
        binaries = entry["binaries"]
        parser = ParserBinaries(
            name=entry["name"],
            mtx2bsp=Path(binaries["mtx2bsp"]),
            bsp2mtx=Path(binaries["bsp2mtx"]),
            check_equivalence=Path(binaries["check_equivalence"]),
            check_canonical_equivalence=(
                Path(binaries["check_canonical_equivalence"])
                if binaries.get("check_canonical_equivalence")
                else None
            ),
            canonical2bsp=(
                Path(binaries["canonical2bsp"])
                if binaries.get("canonical2bsp")
                else None
            ),
        )
        parsers[parser.name] = parser
    return parsers
