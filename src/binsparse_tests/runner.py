from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .contracts import MatrixFixture
from .contracts import ParserBinaries
from .downloads import extract_matrix_market_file
from .downloads import fetch_binsparse_file
from .downloads import fetch_matrix_market_archive


@dataclass(frozen=True)
class CommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_command(*args: str) -> CommandResult:
    completed = subprocess.run(
        args,
        check=False,
        capture_output=True,
        text=True,
    )
    result = CommandResult(
        args=tuple(args),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if result.returncode != 0:
        rendered = " ".join(result.args)
        raise RuntimeError(
            f"command failed: {rendered}\n"
            f"exit code: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def roundtrip_from_matrix_market(
    fixture: MatrixFixture,
    parser: ParserBinaries,
    cache_dir: Path,
    work_dir: Path,
) -> None:
    archive_path = fetch_matrix_market_archive(fixture, cache_dir)
    source_mtx = extract_matrix_market_file(fixture, archive_path, work_dir / "inputs")
    generated_bsp = work_dir / f"{fixture.name}.generated.bsp.h5"
    regenerated_mtx = work_dir / f"{fixture.name}.regenerated.mtx"

    run_command(str(parser.mtx2bsp), str(source_mtx), str(generated_bsp))
    run_command(str(parser.check_equivalence), str(source_mtx), str(generated_bsp))
    run_command(str(parser.bsp2mtx), str(generated_bsp), str(regenerated_mtx))
    run_command(
        str(parser.check_equivalence), str(source_mtx), str(regenerated_mtx)
    )


def roundtrip_from_binsparse(
    fixture: MatrixFixture,
    parser: ParserBinaries,
    cache_dir: Path,
    work_dir: Path,
) -> None:
    source_bsp = fetch_binsparse_file(fixture, cache_dir)
    generated_mtx = work_dir / f"{fixture.name}.generated.mtx"
    regenerated_bsp = work_dir / f"{fixture.name}.regenerated.bsp.h5"

    source_bsp_arg = str(source_bsp)
    if fixture.binsparse.dataset:
        source_bsp_arg = f"{source_bsp}:{fixture.binsparse.dataset}"

    run_command(str(parser.bsp2mtx), source_bsp_arg, str(generated_mtx))
    run_command(str(parser.check_equivalence), source_bsp_arg, str(generated_mtx))
    run_command(str(parser.mtx2bsp), str(generated_mtx), str(regenerated_bsp))
    run_command(str(parser.check_equivalence), source_bsp_arg, str(regenerated_bsp))

