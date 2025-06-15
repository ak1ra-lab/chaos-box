# PYTHON_ARGCOMPLETE_OK

import argparse
import shutil
import tarfile
from pathlib import Path

import argcomplete

# apt install python3-debian
# pdm venv create: venv_args, additional arguments that will be passed to the backend
# pdm venv create -- 3.11 --system-site-packages
from debian import arfile

from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


class DebExtractor:
    def __init__(self, delete_mode=False):
        self.delete_mode = delete_mode
        self.cwd = Path.cwd()

    def process_deb(self, deb_path: Path):
        extract_dir = self.cwd / deb_path.stem

        if self.delete_mode:
            self._remove_extracted(extract_dir)
        else:
            self._extract_deb(deb_path, extract_dir)

    def _extract_deb(self, deb_path: Path, extract_dir: Path):
        if extract_dir.exists():
            logger.info("Skipping '%s' (already extracted)", deb_path.name)
            return

        try:
            with open(deb_path, "rb") as f:
                ar = arfile.ArFile(fileobj=f)
                self._extract_ar_members(ar, extract_dir)
            logger.info(
                "Successfully extracted '%s' to '%s'", deb_path.name, extract_dir
            )
        except (OSError, arfile.ArError, tarfile.TarError, NotImplementedError) as err:
            shutil.rmtree(extract_dir, ignore_errors=True)
            logger.error("Failed to process '%s': '%s'", deb_path.name, err)

    def _extract_ar_members(self, ar: arfile.ArFile, extract_dir: Path):
        control_dir = extract_dir / "control"
        data_dir = extract_dir / "data"

        for member in ar.getmembers():
            if member.name.startswith("control.tar"):
                self._extract_ar_member(member, control_dir)
            elif member.name.startswith("data.tar"):
                self._extract_ar_member(member, data_dir)

    def _extract_ar_member(self, member: arfile.ArMember, extract_dir: Path):
        if member.name.endswith(".tar.zst"):
            logger.warning("Skipping '%s'", member.name)
            raise NotImplementedError("Zstandard compression is not implemented yet")

        extract_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=member) as tar:
            tar.extractall(path=extract_dir)
        logger.debug("Extracted '%s' to '%s'", member.name, extract_dir)

    def _remove_extracted(self, extract_dir: Path):
        if extract_dir.exists() and extract_dir.is_dir():
            try:
                shutil.rmtree(extract_dir)
                logger.info("Successfully removed '%s'", extract_dir)
            except OSError as err:
                logger.error("Failed to remove '%s': '%s'", extract_dir, err)

    def run(self):
        deb_files = sorted(self.cwd.glob("*.deb"))
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
        "-d",
        "--delete",
        action="store_true",
        help="Remove extracted directories instead of extracting",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    extractor = DebExtractor(delete_mode=args.delete)
    extractor.run()


if __name__ == "__main__":
    main()
