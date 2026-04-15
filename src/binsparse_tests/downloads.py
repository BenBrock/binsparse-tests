from __future__ import annotations

import shutil
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

from .contracts import CanonicalFixture
from .contracts import CanonicalReferenceSpec
from .contracts import MatrixFixture


def _download(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination

    with urllib.request.urlopen(url) as response:
        with destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    return destination


def _filename_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    return Path(path).name


def _resolve_local_path(path: str) -> Path:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"source file does not exist: {resolved}")
    return resolved


def fetch_matrix_market_file(
    fixture: MatrixFixture, cache_dir: Path, destination_dir: Path
) -> Path:
    if fixture.matrix_market is None:
        raise ValueError(f"fixture '{fixture.name}' does not define matrix_market")

    return fetch_matrix_market_spec(fixture.matrix_market, cache_dir, destination_dir)


def fetch_matrix_market_spec(
    spec,
    cache_dir: Path,
    destination_dir: Path,
) -> Path:
    if spec.path is not None:
        return _resolve_local_path(spec.path)

    if spec.url is None:
        raise ValueError("matrix_market spec must define either url or path")

    if spec.archive_member is None:
        return _download(spec.url, cache_dir / _filename_from_url(spec.url))

    archive_path = _download(spec.url, cache_dir / _filename_from_url(spec.url))
    return extract_matrix_market_file(spec.archive_member, archive_path, destination_dir)


def fetch_binsparse_file(fixture: MatrixFixture, cache_dir: Path) -> Path:
    if fixture.binsparse.path is not None:
        return _resolve_local_path(fixture.binsparse.path)

    if fixture.binsparse.url is None:
        raise ValueError(
            f"fixture '{fixture.name}' binsparse must define either url or path"
        )

    return _download(
        fixture.binsparse.url,
        cache_dir / _filename_from_url(fixture.binsparse.url),
    )


def fetch_canonical_file(fixture: CanonicalFixture, cache_dir: Path) -> Path:
    if fixture.canonical.path is not None:
        return _resolve_local_path(fixture.canonical.path)

    if fixture.canonical.url is None:
        raise ValueError(
            f"fixture '{fixture.name}' canonical file must define either url or path"
        )

    return _download(
        fixture.canonical.url,
        cache_dir / _filename_from_url(fixture.canonical.url),
    )


def fetch_reference_file(
    fixture: CanonicalFixture,
    reference: CanonicalReferenceSpec,
    cache_dir: Path,
) -> Path:
    if reference.path is not None:
        return _resolve_local_path(reference.path)

    if reference.url is None:
        raise ValueError(
            f"fixture '{fixture.name}' reference '{reference.format}' must define either url or path"
        )

    return _download(reference.url, cache_dir / _filename_from_url(reference.url))


def extract_matrix_market_file(
    archive_member: str, archive_path: Path, destination_dir: Path
) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extract(
            archive_member,
            path=destination_dir,
            filter="data",
        )
    return destination_dir / archive_member
