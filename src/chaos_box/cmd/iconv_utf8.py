# PYTHON_ARGCOMPLETE_OK

import argparse
from pathlib import Path

import argcomplete
import chardet

from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


def detect_encoding(file_path: Path, num_bytes: int = 4096) -> str:
    with open(file_path, "rb") as f:
        raw_data = f.read(num_bytes)
    result = chardet.detect(raw_data)
    logger.debug("Detected encoding for %s: %s", file_path, result)
    return result.get("encoding")


def convert_to_utf8(input_path: Path, dry_run: bool):
    encoding = detect_encoding(input_path)
    if encoding.lower() in ("utf-8", "utf8"):
        logger.info("[SKIP   ] %s is already UTF-8 encoded", input_path)
        return

    output_path = input_path.with_stem(input_path.stem + "-utf8")
    if not encoding:
        logger.warning("Failed to detect encoding for %s", input_path)
        return

    if dry_run:
        logger.info(
            "[DRY RUN] %s (%s)\n        → %s", input_path, encoding, output_path
        )
        return

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
        logger.error("[FAIL   ] %s (%s): %s", input_path, encoding, err)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="perform a dry run without writing files",
    )
    parser.add_argument(
        "-r",
        "--root",
        type=Path,
        default=Path("."),
        help="root directory for rglob, default is current directory",
    )
    parser.add_argument(
        "-g",
        "--glob",
        type=str,
        default="*.chs.srt",
        help="glob pattern for input files, default is '%(default)s'",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    root = args.root.expanduser()
    for input_path in root.rglob(args.glob):
        convert_to_utf8(input_path, args.dry_run)


if __name__ == "__main__":
    main()
