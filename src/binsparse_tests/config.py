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
        fixtures.append(
            MatrixFixture(
                name=entry["name"],
                matrix_market=MatrixMarketSpec(**entry["matrix_market"]),
                binsparse=BinsparseSpec(**entry["binsparse"]),
            )
        )
    return fixtures


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

