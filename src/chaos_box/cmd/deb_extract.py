# PYTHON_ARGCOMPLETE_OK

import argparse
import shutil
import tarfile
from pathlib import Path

import argcomplete
import unix_ar

from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


class DebExtractor:
    def __init__(self, directory: Path, delete_mode: bool = False):
        self.directory = directory
        self.delete_mode = delete_mode

    def _extract_deb(self, deb_path: Path, extract_dir: Path):
        if extract_dir.exists():
            logger.info("Skipping '%s' (already extracted)", deb_path.name)
            return

        try:
            # TypeError: 'ArFile' object does not support the context manager protocol
            ar_file = unix_ar.open(deb_path)
            self._extract_ar_members(ar_file, extract_dir)
            logger.info(
                "Successfully extracted '%s' to '%s'", deb_path.name, extract_dir
            )
            ar_file.close()
        except (OSError, tarfile.TarError) as err:
            shutil.rmtree(extract_dir, ignore_errors=True)
            logger.error("Failed to process '%s': '%s'", deb_path.name, err)

    def _extract_ar_members(self, ar_file: unix_ar.ArFile, extract_dir: Path):
        for ar_info in ar_file.infolist():
            name = ar_info.name.decode()
            if name.startswith("control.tar"):
                self._extract_ar_member(ar_file, name, extract_dir / "control")
            elif name.startswith("data.tar"):
                self._extract_ar_member(ar_file, name, extract_dir / "data")

    def _extract_ar_member(self, ar_file: unix_ar.ArFile, name: str, extract_dir: Path):
        if name.endswith(".tar.zst"):
            logger.warning("Skip '%s', zstd is not implemented yet", name)
            return

        extract_dir.mkdir(parents=True, exist_ok=True)
        tarball = ar_file.open(name)
        with tarfile.open(fileobj=tarball) as tar:
            tar.extractall(path=extract_dir)
        logger.debug("Extracted '%s' to '%s'", name, extract_dir)
        tarball.close()

    def _remove_extracted(self, extract_dir: Path):
        if extract_dir.exists() and extract_dir.is_dir():
            try:
                shutil.rmtree(extract_dir)
                logger.info("Successfully removed '%s'", extract_dir)
            except OSError as err:
                logger.error("Failed to remove '%s': '%s'", extract_dir, err)

    def process_deb(self, deb_path: Path):
        extract_dir = self.directory / deb_path.stem

        if self.delete_mode:
            self._remove_extracted(extract_dir)
        else:
            self._extract_deb(deb_path, extract_dir)

    def run(self):
        deb_files = sorted(self.directory.glob("*.deb"))
        if not deb_files:
            logger.warning("No .deb files found in current directory")
            return

        logger.info("Found %d .deb file(s) to process", len(deb_files))
        for deb_file in deb_files:
            self.process_deb(deb_file)


def main():
    parser = argparse.ArgumentParser(
        description="Debian package extractor",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Remove extracted directories instead of extracting",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    directory = Path(args.directory)
    extractor = DebExtractor(directory, delete_mode=args.delete)
    extractor.run()


if __name__ == "__main__":
    main()
