from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .contracts import CanonicalFixture
from .contracts import CanonicalReferenceSpec
from .contracts import MatrixFixture
from .contracts import ParserBinaries
from .downloads import fetch_canonical_file
from .downloads import fetch_binsparse_file
from .downloads import fetch_matrix_market_file
from .downloads import fetch_reference_file


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


def _artifact_stem(fixture: MatrixFixture) -> str:
    return fixture.name.replace("/", "__").replace("\\", "__")


def _canonical_artifact_stem(fixture: CanonicalFixture, reference: CanonicalReferenceSpec) -> str:
    name = fixture.name.replace("/", "__").replace("\\", "__")
    return f"{name}.{reference.format.lower()}"


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


def verify_reference_matches_canonical(
    fixture: CanonicalFixture,
    reference: CanonicalReferenceSpec,
    parser: ParserBinaries,
    cache_dir: Path,
) -> None:
    if parser.check_canonical_equivalence is None:
        raise RuntimeError(
            f"parser '{parser.name}' does not define check_canonical_equivalence"
        )

    canonical_path = fetch_canonical_file(fixture, cache_dir)
    reference_path = fetch_reference_file(fixture, reference, cache_dir)
    reference_arg = str(reference_path)
    if reference.dataset:
        reference_arg = f"{reference_arg}:{reference.dataset}"

    run_command(
        str(parser.check_canonical_equivalence),
        str(canonical_path),
        reference_arg,
    )


def generate_from_canonical_and_compare(
    fixture: CanonicalFixture,
    reference: CanonicalReferenceSpec,
    parser: ParserBinaries,
    cache_dir: Path,
    work_dir: Path,
) -> None:
    if parser.canonical2bsp is None:
        raise RuntimeError(f"parser '{parser.name}' does not define canonical2bsp")

    if parser.check_canonical_equivalence is None:
        raise RuntimeError(
            f"parser '{parser.name}' does not define check_canonical_equivalence"
        )

    canonical_path = fetch_canonical_file(fixture, cache_dir)
    reference_path = fetch_reference_file(fixture, reference, cache_dir)

    artifact_stem = _canonical_artifact_stem(fixture, reference)
    generated_bsp = work_dir / f"{artifact_stem}.generated.bsp.h5"
    if reference.dataset:
        generated_arg = f"{generated_bsp}:{reference.dataset}"
    else:
        generated_arg = str(generated_bsp)

    if reference.dataset:
        generated_bsp.parent.mkdir(parents=True, exist_ok=True)
        if generated_bsp.exists():
            generated_bsp.unlink()

    run_command(
        str(parser.canonical2bsp),
        str(canonical_path),
        generated_arg,
        reference.format,
    )
    run_command(
        str(parser.check_canonical_equivalence),
        str(canonical_path),
        generated_arg,
    )

    reference_arg = str(reference_path)
    if reference.dataset:
        reference_arg = f"{reference_arg}:{reference.dataset}"

    run_command(str(parser.check_equivalence), reference_arg, generated_arg)
