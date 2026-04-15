from __future__ import annotations

from pathlib import Path

from .commands import run_command
from .contracts import MatrixFixture
from .contracts import ParserBinaries
from .downloads import fetch_binsparse_file
from .downloads import fetch_matrix_market_file


def _artifact_stem(fixture: MatrixFixture) -> str:
    return fixture.name.replace("/", "__").replace("\\", "__")


def roundtrip_from_matrix_market(
    fixture: MatrixFixture,
    parser: ParserBinaries,
    cache_dir: Path,
    work_dir: Path,
) -> None:
    source_mtx = fetch_matrix_market_file(fixture, cache_dir, work_dir / "inputs")
    artifact_stem = _artifact_stem(fixture)
    generated_bsp = work_dir / f"{artifact_stem}.generated.bsp.h5"
    regenerated_mtx = work_dir / f"{artifact_stem}.regenerated.mtx"

    run_command(str(parser.mtx2bsp), str(source_mtx), str(generated_bsp))
    run_command(str(parser.check_equivalence), str(source_mtx), str(generated_bsp))
    run_command(str(parser.bsp2mtx), str(generated_bsp), str(regenerated_mtx))
    run_command(str(parser.check_equivalence), str(source_mtx), str(regenerated_mtx))


def roundtrip_from_binsparse(
    fixture: MatrixFixture,
    parser: ParserBinaries,
    cache_dir: Path,
    work_dir: Path,
) -> None:
    source_bsp = fetch_binsparse_file(fixture, cache_dir)
    artifact_stem = _artifact_stem(fixture)
    generated_mtx = work_dir / f"{artifact_stem}.generated.mtx"
    regenerated_bsp = work_dir / f"{artifact_stem}.regenerated.bsp.h5"

    source_bsp_arg = str(source_bsp)
    if fixture.binsparse.dataset:
        source_bsp_arg = f"{source_bsp}:{fixture.binsparse.dataset}"

    run_command(str(parser.bsp2mtx), source_bsp_arg, str(generated_mtx))
    run_command(str(parser.check_equivalence), source_bsp_arg, str(generated_mtx))
    run_command(str(parser.mtx2bsp), str(generated_mtx), str(regenerated_bsp))
    run_command(str(parser.check_equivalence), source_bsp_arg, str(regenerated_bsp))
