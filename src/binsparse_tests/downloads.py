from __future__ import annotations

import shutil
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

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


def fetch_matrix_market_archive(fixture: MatrixFixture, cache_dir: Path) -> Path:
    return _download(
        fixture.matrix_market.url,
        cache_dir / _filename_from_url(fixture.matrix_market.url),
    )


def fetch_binsparse_file(fixture: MatrixFixture, cache_dir: Path) -> Path:
    return _download(
        fixture.binsparse.url,
        cache_dir / _filename_from_url(fixture.binsparse.url),
    )


def extract_matrix_market_file(
    fixture: MatrixFixture, archive_path: Path, destination_dir: Path
) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extract(
            fixture.matrix_market.archive_member,
            path=destination_dir,
            filter="data",
        )
    return destination_dir / fixture.matrix_market.archive_member
