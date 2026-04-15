from __future__ import annotations

from pathlib import Path

import pytest

from binsparse_tests.config import discover_binsparse_fixtures
from binsparse_tests.config import load_canonical_manifest
from binsparse_tests.config import load_matrix_manifest
from binsparse_tests.config import load_parser_manifest
from binsparse_tests.contracts import CanonicalReferenceCase


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--matrix-manifest",
        action="store",
        default="config/matrices.json",
        help="Path to the matrix manifest JSON file. Pass '-' to disable it.",
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
    parser.addoption(
        "--binsparse-root",
        action="store",
        default=None,
        help="Discover local binsparse fixtures under this directory.",
    )
    parser.addoption(
        "--canonical-manifest",
        action="store",
        default="config/canonical_matrices.json",
        help="Path to the canonical HDF5 fixture manifest JSON file. Pass '-' to disable it.",
    )


def _load_requested_fixtures(pytestconfig: pytest.Config) -> list:
    fixtures = []
    requested_sources = False

    manifest_arg = pytestconfig.getoption("--matrix-manifest")
    if manifest_arg not in (None, "", "-", "none"):
        requested_sources = True
        manifest_path = Path(manifest_arg)
        if not manifest_path.exists():
            raise pytest.UsageError(f"matrix manifest not found: {manifest_path}")
        fixtures.extend(load_matrix_manifest(manifest_path))

    binsparse_root_arg = pytestconfig.getoption("--binsparse-root")
    if binsparse_root_arg:
        requested_sources = True
        binsparse_root = Path(binsparse_root_arg)
        if not binsparse_root.is_dir():
            raise pytest.UsageError(
                f"binsparse root is not a directory: {binsparse_root}"
            )
        fixtures.extend(discover_binsparse_fixtures(binsparse_root))

    if not fixtures:
        if not requested_sources:
            return []
        raise pytest.UsageError(
            "no matrix fixtures were found; provide --matrix-manifest and/or "
            "--binsparse-root"
        )

    return fixtures


def _load_requested_canonical_fixtures(pytestconfig: pytest.Config) -> list:
    manifest_arg = pytestconfig.getoption("--canonical-manifest")
    if manifest_arg in (None, "", "-", "none"):
        return []

    manifest_path = Path(manifest_arg)
    if not manifest_path.exists():
        raise pytest.UsageError(f"canonical manifest not found: {manifest_path}")

    return load_canonical_manifest(manifest_path)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    fixtures = None
    canonical_fixtures = None

    if "matrix_fixture" in metafunc.fixturenames:
        fixtures = fixtures or _load_requested_fixtures(metafunc.config)
        metafunc.parametrize(
            "matrix_fixture",
            fixtures,
            indirect=True,
            ids=[fixture.name for fixture in fixtures],
        )

    if "paired_matrix_fixture" in metafunc.fixturenames:
        fixtures = fixtures or _load_requested_fixtures(metafunc.config)
        paired_fixtures = [
            fixture for fixture in fixtures if fixture.matrix_market is not None
        ]
        metafunc.parametrize(
            "paired_matrix_fixture",
            paired_fixtures,
            indirect=True,
            ids=[fixture.name for fixture in paired_fixtures],
        )

    if "binsparse_fixture" in metafunc.fixturenames:
        fixtures = fixtures or _load_requested_fixtures(metafunc.config)
        metafunc.parametrize(
            "binsparse_fixture",
            fixtures,
            indirect=True,
            ids=[fixture.name for fixture in fixtures],
        )

    if "canonical_fixture" in metafunc.fixturenames:
        canonical_fixtures = canonical_fixtures or _load_requested_canonical_fixtures(
            metafunc.config
        )
        metafunc.parametrize(
            "canonical_fixture",
            canonical_fixtures,
            indirect=True,
            ids=[fixture.name for fixture in canonical_fixtures],
        )

    if "canonical_reference_case" in metafunc.fixturenames:
        canonical_fixtures = canonical_fixtures or _load_requested_canonical_fixtures(
            metafunc.config
        )
        cases = [
            CanonicalReferenceCase(fixture=fixture, reference=reference)
            for fixture in canonical_fixtures
            for reference in fixture.references
        ]
        metafunc.parametrize(
            "canonical_reference_case",
            cases,
            indirect=True,
            ids=[case.id for case in cases],
        )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if not any(
        set(getattr(item, "fixturenames", ()))
        & {"matrix_fixture", "paired_matrix_fixture", "binsparse_fixture"}
        for item in items
    ):
        return

    fixtures = _load_requested_fixtures(config)
    if any(fixture.matrix_market is not None for fixture in fixtures):
        return

    retained = []
    deselected = []
    for item in items:
        if "paired_matrix_fixture" in getattr(item, "fixturenames", ()):
            deselected.append(item)
            continue
        retained.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = retained


@pytest.fixture
def matrix_fixture(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def paired_matrix_fixture(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def binsparse_fixture(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def canonical_fixture(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def canonical_reference_case(request: pytest.FixtureRequest):
    return request.param


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
