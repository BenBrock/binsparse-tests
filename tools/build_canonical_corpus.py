from __future__ import annotations

import argparse
from pathlib import Path

from binsparse_tests.canonical import matrix_market_to_canonical
from binsparse_tests.canonical import write_canonical_hdf5
from binsparse_tests.commands import run_command
from binsparse_tests.config import load_canonical_manifest
from binsparse_tests.config import load_parser_manifest
from binsparse_tests.downloads import fetch_matrix_market_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build canonical dense HDF5 fixtures and optional binsparse references."
    )
    parser.add_argument(
        "--manifest",
        default="config/canonical_matrices.json",
        help="Path to the canonical fixture manifest.",
    )
    parser.add_argument(
        "--artifact-cache",
        default=".pytest_cache/binsparse-tests",
        help="Directory for cached source downloads.",
    )
    parser.add_argument(
        "--parser-config",
        default=None,
        help="Optional parser config used to generate reference binsparse files.",
    )
    parser.add_argument(
        "--parser",
        default=None,
        help="Parser name from --parser-config used to generate reference files.",
    )
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Specific canonical fixture name(s) to build. Defaults to every fixture in the manifest.",
    )
    parser.add_argument(
        "--compression-level",
        type=int,
        default=9,
        help="Gzip compression level for canonical HDF5 files.",
    )
    parser.add_argument(
        "--skip-references",
        action="store_true",
        help="Only build canonical HDF5 files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    fixtures = load_canonical_manifest(manifest_path)
    requested = set(args.fixture)
    if requested:
        fixtures = [fixture for fixture in fixtures if fixture.name in requested]

    if not fixtures:
        raise SystemExit("no canonical fixtures selected")

    cache_dir = Path(args.artifact_cache)
    parser = None
    if not args.skip_references:
        if args.parser_config is None:
            raise SystemExit("--parser-config is required unless --skip-references is set")
        parsers = load_parser_manifest(Path(args.parser_config))
        parser_name = args.parser or next(iter(parsers))
        parser = parsers[parser_name]
        if parser.canonical2bsp is None:
            raise SystemExit(f"parser '{parser_name}' does not define canonical2bsp")

    for fixture in fixtures:
        source_path = fetch_matrix_market_spec(
            fixture.suite_sparse,
            cache_dir=cache_dir,
            destination_dir=cache_dir / "suitesparse",
        )
        canonical = matrix_market_to_canonical(
            source_path,
            name=fixture.name,
            source_url=fixture.suite_sparse.url,
            source_archive_member=fixture.suite_sparse.archive_member,
        )
        canonical_path = Path(fixture.canonical.path or fixture.canonical.url or "")
        if not canonical_path:
            raise SystemExit(f"fixture '{fixture.name}' does not define a canonical path")
        write_canonical_hdf5(
            canonical_path,
            canonical,
            compression_level=args.compression_level,
        )
        print(f"wrote canonical fixture: {canonical_path}")

        if parser is None:
            continue

        for reference in fixture.references:
            reference_path = Path(reference.path or reference.url or "")
            if not reference_path:
                raise SystemExit(
                    f"fixture '{fixture.name}' reference '{reference.format}' does not define a path"
                )
            reference_path.parent.mkdir(parents=True, exist_ok=True)
            target = str(reference_path)
            if reference.dataset:
                target = f"{target}:{reference.dataset}"
            run_command(
                str(parser.canonical2bsp),
                str(canonical_path),
                target,
                reference.format,
            )
            if parser.check_canonical_equivalence is not None:
                run_command(
                    str(parser.check_canonical_equivalence),
                    str(canonical_path),
                    target,
                )
            print(f"wrote reference fixture: {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
