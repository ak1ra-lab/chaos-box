# PYTHON_ARGCOMPLETE_OK

import argparse
import hashlib
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterator, Tuple

import argcomplete

from miscbox.logging import setup_logger

logger = setup_logger(__name__)

DEFAULT_DIGEST = "sha256"
SUPPORTED_DIGESTS = {
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}


def file_digest(file_path: Path, digest: str) -> Tuple[str, Path]:
    """Calculate the hash of a file."""
    try:
        with open(file_path, "rb") as f:
            hexdigest = hashlib.file_digest(f, SUPPORTED_DIGESTS[digest]).hexdigest()
        return (hexdigest, file_path)
    except Exception as err:
        logger.error("Error processing %s: %s", file_path, err)


def find_files(directory: Path) -> Iterator[Path]:
    """Generator that yields all files in a directory recursively."""
    for root, _, files in os.walk(directory):
        for file in files:
            yield Path(root) / file


def process_directory(
    directory: Path, digest: str = DEFAULT_DIGEST, workers: int = None
) -> None:
    """Process all files in a directory to calculate their hashes."""
    output_file = directory.with_name(f"{directory.name}.{digest}sum")
    files = list(find_files(directory))

    if not files:
        logger.warning("No files found in directory: %s", directory)
        return

    logger.info("Processing %d files with %s...", len(files), digest)

    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = executor.map(
                file_digest,
                files,
                [digest] * len(files),
                chunksize=10,  # Balance between overhead and memory usage
            )

        # Sort results by file path
        sorted_results = sorted(results, key=lambda x: x[1])

        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            for hash_value, file_path in sorted_results:
                relative_path = os.path.relpath(file_path, directory)
                f.write(f"{hash_value}  {relative_path}\n")

        logger.info("Results written to: %s", output_file)

    except Exception as err:
        logger.error("Error during processing: %s", err)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate file hashes for all files in a directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-d",
        "--digest",
        choices=SUPPORTED_DIGESTS.keys(),
        default=DEFAULT_DIGEST,
        help=f"Hash algorithm to use (default: {DEFAULT_DIGEST})",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=None,
        help="Number of parallel jobs (default: number of CPU cores)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main():
    args = parse_args()

    try:
        directory = Path(args.directory).resolve()
        if not directory.is_dir():
            raise ValueError("Not a directory: %s", directory)

        logger.debug("Processing directory: %s", directory)
        logger.debug("Using hash algorithm: %s", args.digest)
        logger.debug("Using %s workers", args.jobs or "auto")

        process_directory(directory, args.digest, args.jobs)

    except Exception as err:
        logger.error(err)


if __name__ == "__main__":
    main()
