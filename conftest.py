from __future__ import annotations

from pathlib import Path

import pytest

from binsparse_tests.pytest_support import filter_legacy_collection
from binsparse_tests.pytest_support import load_active_parser
from binsparse_tests.pytest_support import parametrize_requested_fixtures
from binsparse_tests.pytest_support import register_pytest_options


def pytest_addoption(parser: pytest.Parser) -> None:
    register_pytest_options(parser)


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    parametrize_requested_fixtures(metafunc)


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    filter_legacy_collection(config, items)


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
    return load_active_parser(pytestconfig)
