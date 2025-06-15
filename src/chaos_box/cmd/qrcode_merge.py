# PYTHON_ARGCOMPLETE_OK

import argparse
import base64
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import argcomplete
from PIL import Image
from pyzbar.pyzbar import decode

from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


def decode_qr_code(file_path: Path) -> tuple[int, str] | None:
    try:
        img = Image.open(file_path)
        decoded_objects = decode(img)
        if decoded_objects:
            data = decoded_objects[0].data.decode("utf-8")
            index = int(file_path.stem.split("_")[-1])
            return (index, data)
        else:
            return None
    except Exception as err:
        logger.info("Error decoding %s: %s", file_path, err)
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a directory of QR code images back into the original file."
    )
    parser.add_argument(
        "directory", help="Path to the directory containing the QR code images."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to save the merged file."
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: number of CPU cores)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main():
    args = parse_args()

    directory = Path(args.directory)
    if not (directory.exists() and directory.is_dir()):
        logger.error("The specified directory does not exist: %s", directory)
        return

    qr_files = []
    for f in directory.glob("*.png"):
        try:
            int(f.stem.split("_")[-1])
            qr_files.append(f)
        except Exception:
            logger.warning("Skip file with unexpected name: %s", f)
            continue

    if not qr_files:
        logger.error("No valid QR code images found in %s", directory)
        return

    qr_files.sort(key=lambda f: int(f.stem.split("_")[-1]))

    decoded_chunks = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(decode_qr_code, f): f for f in qr_files}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                decoded_chunks.append(result)

    if not decoded_chunks:
        logger.error("No QR code could be decoded successfully.")
        return

    decoded_chunks.sort(key=lambda x: x[0])  # Sort by index

    data_chunks = []
    for idx, chunk in decoded_chunks:
        try:
            data_chunks.append(base64.b64decode(chunk))
        except Exception as err:
            logger.error("Base64 decode failed for chunk %s: %s", idx, err)
            continue

    if not data_chunks:
        logger.error("No valid data chunks to write.")
        return

    with open(args.output, "wb") as f:
        for chunk in data_chunks:
            f.write(chunk)

    logger.info("Merged file saved to %s", args.output)


if __name__ == "__main__":
    main()
