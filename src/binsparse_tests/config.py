from __future__ import annotations

import json
from pathlib import Path

from .contracts import BinsparseSpec
from .contracts import MatrixFixture
from .contracts import MatrixMarketSpec
from .contracts import ParserBinaries


def load_matrix_manifest(path: Path) -> list[MatrixFixture]:
    payload = json.loads(path.read_text())
    fixtures: list[MatrixFixture] = []
    for entry in payload["matrices"]:
        matrix_market = None
        if entry.get("matrix_market") is not None:
            matrix_market = MatrixMarketSpec(**entry["matrix_market"])
        fixtures.append(
            MatrixFixture(
                name=entry["name"],
                matrix_market=matrix_market,
                binsparse=BinsparseSpec(**entry["binsparse"]),
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
        )
        parsers[parser.name] = parser
    return parsers
