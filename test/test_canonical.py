from __future__ import annotations

from pathlib import Path

import pytest

from binsparse_tests.runner import generate_from_canonical_and_compare
from binsparse_tests.runner import verify_reference_matches_canonical


def test_reference_matches_canonical(
    canonical_reference_case,
    active_parser,
    artifact_cache: Path,
) -> None:
    if active_parser.check_canonical_equivalence is None:
        pytest.skip(
            f"parser '{active_parser.name}' does not provide check_canonical_equivalence"
        )

    verify_reference_matches_canonical(
        fixture=canonical_reference_case.fixture,
        reference=canonical_reference_case.reference,
        parser=active_parser,
        cache_dir=artifact_cache,
    )


def test_generate_from_canonical(
    canonical_reference_case,
    active_parser,
    artifact_cache: Path,
    tmp_path: Path,
) -> None:
    if active_parser.canonical2bsp is None:
        pytest.skip(f"parser '{active_parser.name}' does not provide canonical2bsp")
    if active_parser.check_canonical_equivalence is None:
        pytest.skip(
            f"parser '{active_parser.name}' does not provide check_canonical_equivalence"
        )

    generate_from_canonical_and_compare(
        fixture=canonical_reference_case.fixture,
        reference=canonical_reference_case.reference,
        parser=active_parser,
        cache_dir=artifact_cache,
        work_dir=tmp_path,
    )
