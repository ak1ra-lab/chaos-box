# PYTHON_ARGCOMPLETE_OK

import argparse
from pathlib import Path

import argcomplete
import chardet

from chaos_box.gitignore import rglob_respect_gitignore
from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


skipped_files = set()
failed_files = set()


def detect_encoding(file_path: Path, num_bytes: int = 4096) -> str:
    with open(file_path, "rb") as f:
        raw_data = f.read(num_bytes)
    result = chardet.detect(raw_data)
    logger.debug("Detected encoding for %s: %s", file_path, result)
    return result.get("encoding")


def convert_to_utf8(input_path: Path, output_path: Path, dry_run: bool, force: bool):
    encoding = detect_encoding(input_path)
    if encoding.lower() in ("utf-8", "utf8"):
        skipped_files.add(input_path)
        logger.info("[SKIP   ] %s is already UTF-8 encoded", input_path)
        return

    if not encoding:
        logger.warning("Failed to detect encoding for %s", input_path)
        return

    if dry_run:
        logger.info(
            "[DRY RUN] %s (%s)\n        → %s", input_path, encoding, output_path
        )
        return

    if output_path.exists() and not force:
        logger.warning(
            "[SKIP   ] Output file %s already exists. Use --force to overwrite.",
            output_path,
        )
        return

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        chunk_size = 1024 * 1024  # 1MB
        with (
            open(input_path, "r", encoding=encoding, errors="replace") as src,
            open(output_path, "w", encoding="utf-8") as dest,
        ):
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                dest.write(chunk)
        logger.info(
            "[OK     ] %s (%s)\n        → %s", input_path, encoding, output_path
        )
    except Exception as err:
        failed_files.add(input_path)
        logger.error("[FAIL   ] %s (%s): %s", input_path, encoding, err)


def parse_args():
    parser = argparse.ArgumentParser(description="convert text files to UTF-8 encoding")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="root directory for rglob, default is current directory",
    )
    parser.add_argument(
        "--glob",
        type=str,
        default="*.chs.srt",
        help="glob pattern for input files, default is '%(default)s'",
    )
    parser.add_argument(
        "--gitignore",
        action="store_true",
        help="respect .gitignore files when searching for input files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="output directory for converted files, default is the same directory as input files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="force overwrite of existing output files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="perform a dry run without writing files",
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).expanduser()
    output_dir = Path(args.output_dir).expanduser() if args.output_dir else None

    if args.gitignore:
        input_files = rglob_respect_gitignore(root, args.glob)
    else:
        input_files = root.rglob(args.glob)

    for input_path in input_files:
        output_path = input_path.with_stem(input_path.stem + "-utf8")
        if output_dir:
            output_path = output_dir / output_path.relative_to(root)

        convert_to_utf8(input_path, output_path, args.dry_run, args.force)

    if len(skipped_files) > 0:
        logger.info(
            "Skipped %d files that are already UTF-8 encoded:\n    %s",
            len(skipped_files),
            "\n    ".join(str(f) for f in skipped_files),
        )
    if len(failed_files) > 0:
        logger.error(
            "Failed to convert %d files:\n    %s",
            len(failed_files),
            "\n    ".join(str(f) for f in failed_files),
        )


if __name__ == "__main__":
    main()
