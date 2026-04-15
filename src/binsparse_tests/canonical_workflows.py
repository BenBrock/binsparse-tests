from __future__ import annotations

from pathlib import Path

from .commands import run_command
from .contracts import CanonicalFixture
from .contracts import CanonicalReferenceSpec
from .contracts import ParserBinaries
from .downloads import fetch_canonical_file
from .downloads import fetch_reference_file


def _canonical_artifact_stem(
    fixture: CanonicalFixture, reference: CanonicalReferenceSpec
) -> str:
    name = fixture.name.replace("/", "__").replace("\\", "__")
    return f"{name}.{reference.format.lower()}"


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
    generated_arg = str(generated_bsp)
    if reference.dataset:
        generated_arg = f"{generated_arg}:{reference.dataset}"

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
