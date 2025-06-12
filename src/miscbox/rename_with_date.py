# PYTHON_ARGCOMPLETE_OK

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import argcomplete

from miscbox.logging import setup_logger

logger = setup_logger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {".md", ".txt", ".png", ".pdf", ".drawio", ".canvas"}
# Regex pattern for existing date prefixes
DATE_PREFIX_REGEX = re.compile(r"^(([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2})-)?")


def find_files(directory: str) -> List[Path]:
    """Find all supported files in the directory tree."""
    directory_path = Path(directory).resolve()
    files = []

    for item in directory_path.rglob("*"):
        if not (item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS):
            continue
        try:
            files.append(item.relative_to(directory_path))
        except ValueError:
            logger.debug("Skipping file outside working directory: %s", item)
            continue

    return files


def get_dest_filename(src_path: Path) -> Tuple[Path, bool]:
    """Generate new filename with last modified date prefix."""
    mtime = src_path.stat().st_mtime
    date_prefix = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    # Remove any existing date prefix
    dest_basename_no_prefix = DATE_PREFIX_REGEX.sub("", src_path.name)

    dest_basename = f"{date_prefix}-{dest_basename_no_prefix}"
    dest_path = src_path.parent / dest_basename

    return dest_path, (dest_path != src_path)


def process_files(files: List[Path], apply: bool = False) -> None:
    """Process files by either renaming them or logging the changes in dry-run mode."""
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
    parser.add_argument("directory", help="Directory containing files to process")
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

    directory = args.directory
    if not Path(directory).exists():
        logger.error("Directory '%s' does not exist", directory)
        return

    files = find_files(directory)
    if not files:
        logger.warning("No supported files found in '%s'", directory)
        return

    logger.info("Found %d files to process", len(files))
    if not args.apply:
        logger.info("Running in dry-run mode - no changes will be made")

    process_files(files, args.apply)
    logger.info("Processing complete")


if __name__ == "__main__":
    main()
