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

from miscbox.logging import setup_logger

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
            logger.info(f"Skipping {deb_path.name} (already extracted)")
            return

        try:
            with open(deb_path, "rb") as f:
                ar = arfile.ArFile(fileobj=f)
                self._extract_ar_contents(ar, extract_dir)
            logger.info(f"Successfully extracted {deb_path.name} to {extract_dir}")
        except (OSError, arfile.ArError, tarfile.TarError) as e:
            shutil.rmtree(extract_dir, ignore_errors=True)
            logger.error(f"Failed to process {deb_path.name}: {str(e)}", exc_info=True)

    def _extract_ar_contents(self, ar: arfile.ArFile, extract_dir: Path):
        control_dir = extract_dir / "control"
        data_dir = extract_dir / "data"

        control_dir.mkdir(parents=True)
        data_dir.mkdir()

        for member in ar.getmembers():
            if member.name.startswith("control.tar"):
                with tarfile.open(fileobj=ar.extractfile(member)) as tar:
                    tar.extractall(path=control_dir)
                logger.debug(f"Extracted control files to {control_dir}")
            elif member.name.startswith("data.tar"):
                with tarfile.open(fileobj=ar.extractfile(member)) as tar:
                    tar.extractall(path=data_dir)
                logger.debug(f"Extracted data files to {data_dir}")

    def _remove_extracted(self, extract_dir: Path):
        if extract_dir.exists() and extract_dir.is_dir():
            try:
                shutil.rmtree(extract_dir)
                logger.info(f"Successfully removed {extract_dir}")
            except OSError as e:
                logger.error(f"Failed to remove {extract_dir}: {str(e)}", exc_info=True)

    def run(self):
        deb_files = sorted(self.cwd.glob("*.deb"))
        if not deb_files:
            logger.warning("No .deb files found in current directory")
            return

        logger.info(f"Found {len(deb_files)} .deb file(s) to process")
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
