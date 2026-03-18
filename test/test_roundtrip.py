from __future__ import annotations

from pathlib import Path

from binsparse_tests.runner import roundtrip_from_binsparse
from binsparse_tests.runner import roundtrip_from_matrix_market


def test_roundtrip_from_matrix_market(
    matrix_fixture,
    active_parser,
    artifact_cache: Path,
    tmp_path: Path,
) -> None:
    roundtrip_from_matrix_market(
        fixture=matrix_fixture,
        parser=active_parser,
        cache_dir=artifact_cache,
        work_dir=tmp_path,
    )


def test_roundtrip_from_binsparse(
    matrix_fixture,
    active_parser,
    artifact_cache: Path,
    tmp_path: Path,
) -> None:
    roundtrip_from_binsparse(
        fixture=matrix_fixture,
        parser=active_parser,
        cache_dir=artifact_cache,
        work_dir=tmp_path,
    )

