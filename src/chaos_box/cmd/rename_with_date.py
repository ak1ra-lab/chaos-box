"""Rename files to include their last modified date as a prefix."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import argcomplete
from chaos_utils.gitignore import rglob_respect_gitignore
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)

# Regex pattern for existing date prefixes
DATE_PREFIX_REGEX = re.compile(r"^(([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2})-)?")


def get_dest_filename(src_path: Path) -> Tuple[Path, bool]:
    """Generate new filename with last modified date prefix.

    Args:
        src_path: Source file path

    Returns:
        Tuple of (new path, should rename)
    """
    mtime = src_path.stat().st_mtime
    date_prefix = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    # Remove any existing date prefix
    dest_basename_no_prefix = DATE_PREFIX_REGEX.sub("", src_path.name)

    dest_basename = f"{date_prefix}-{dest_basename_no_prefix}"
    dest_path = src_path.parent / dest_basename

    return dest_path, (dest_path != src_path)


def process_files(files: List[Path], apply: bool = False) -> None:
    """Process files by either renaming them or logging the changes.

    Args:
        files: List of files to process
        apply: Whether to actually rename files
    """
    for src in files:
        dest, should_rename = get_dest_filename(src)
        if not should_rename:
            continue

        if not apply:
            logger.info("src:  %s\ndest: %s\n", src, dest)
            continue

        try:
            src.rename(dest)
            logger.info("src:  %s\ndest: %s\n", src, dest)
        except OSError as err:
            logger.error("Error renaming %s: %s", src, err)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Rename files with last modified date prefix"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-g",
        "--glob",
        default="*.md",
        help="glob pattern for iter_files, default: '%(default)s'",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the renaming (default is dry-run)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main() -> None:
    """Main function to process files in the given directory."""
    args = parse_args()

    directory = Path(args.directory).resolve()
    if not directory.exists():
        logger.error("Directory '%s' does not exist", directory)
        return

    files = list(
        f.relative_to(directory) for f in rglob_respect_gitignore(directory, args.glob)
    )

    logger.info("Found %d files to process", len(files))
    if not args.apply:
        logger.info("Running in dry-run mode - no changes will be made")

    process_files(files, args.apply)
    logger.info("Processing complete")


if __name__ == "__main__":
    main()
