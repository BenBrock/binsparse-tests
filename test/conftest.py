from __future__ import annotations

from pathlib import Path

import pytest

from binsparse_tests.config import load_matrix_manifest
from binsparse_tests.config import load_parser_manifest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--matrix-manifest",
        action="store",
        default="config/matrices.json",
        help="Path to the matrix manifest JSON file.",
    )
    parser.addoption(
        "--parser-config",
        action="store",
        default="config/parsers.local.json",
        help="Path to the parser config JSON file.",
    )
    parser.addoption(
        "--parser",
        action="store",
        default=None,
        help="Parser name to use from the parser config file.",
    )
    parser.addoption(
        "--artifact-cache",
        action="store",
        default=None,
        help="Directory for downloaded matrix artifacts.",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "matrix_fixture" not in metafunc.fixturenames:
        return

    manifest_path = Path(metafunc.config.getoption("--matrix-manifest"))
    fixtures = load_matrix_manifest(manifest_path)
    metafunc.parametrize(
        "matrix_fixture",
        fixtures,
        ids=[fixture.name for fixture in fixtures],
    )


@pytest.fixture(scope="session")
def artifact_cache(pytestconfig: pytest.Config) -> Path:
    configured = pytestconfig.getoption("--artifact-cache")
    if configured:
        cache_dir = Path(configured)
    else:
        cache_dir = Path(".pytest_cache") / "binsparse-tests"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


@pytest.fixture(scope="session")
def active_parser(pytestconfig: pytest.Config):
    config_path = Path(pytestconfig.getoption("--parser-config"))
    if not config_path.exists():
        pytest.skip(
            f"parser config not found: {config_path}. "
            "Create it from config/parsers.example.json."
        )

    parser_name = pytestconfig.getoption("--parser")
    parsers = load_parser_manifest(config_path)
    if not parsers:
        pytest.skip(f"no parsers were defined in {config_path}")

    if parser_name is None:
        parser_name = next(iter(parsers))

    if parser_name not in parsers:
        available = ", ".join(sorted(parsers))
        raise pytest.UsageError(
            f"unknown parser '{parser_name}'. Available parsers: {available}"
        )

    parser = parsers[parser_name]
    missing = [
        path
        for path in (
            parser.mtx2bsp,
            parser.bsp2mtx,
            parser.check_equivalence,
        )
        if not path.exists()
    ]
    if missing:
        joined = ", ".join(str(path) for path in missing)
        pytest.skip(f"parser binaries do not exist: {joined}")

    return parser

