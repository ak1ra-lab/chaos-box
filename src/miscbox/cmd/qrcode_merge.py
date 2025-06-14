# PYTHON_ARGCOMPLETE_OK

import argparse
import base64
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import argcomplete
from PIL import Image
from pyzbar.pyzbar import decode

from miscbox.logging import setup_logger

logger = setup_logger(__name__)


def decode_qr_code(file_path):
    try:
        img = Image.open(file_path)
        decoded_objects = decode(img)
        if decoded_objects:
            data = decoded_objects[0].data.decode("utf-8")
            index = int(os.path.splitext(os.path.basename(file_path))[0].split("_")[-1])
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
        "-o", "--output-file", help="Path to save the merged file.", required=True
    )
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=4,
        help="Number of processes to use.",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isdir(args.directory):
        raise ValueError(f"The specified directory does not exist: {args.directory}")

    qr_files = [
        os.path.join(args.directory, f)
        for f in os.listdir(args.directory)
        if f.endswith(".png")
    ]
    qr_files.sort(
        key=lambda f: int(os.path.splitext(os.path.basename(f))[0].split("_")[-1])
    )  # Sort by index

    decoded_chunks = []
    with ProcessPoolExecutor(max_workers=args.processes) as executor:
        future_to_file = {executor.submit(decode_qr_code, f): f for f in qr_files}
        for future in as_completed(future_to_file):
            result = future.result()
            if result is not None:
                decoded_chunks.append(result)

    decoded_chunks.sort(key=lambda x: x[0])  # Sort by index
    data_chunks = [base64.b64decode(chunk) for _, chunk in decoded_chunks]

    with open(args.output_file, "wb") as f:
        for chunk in data_chunks:
            f.write(chunk)

    logger.info("Merged file saved to %s", args.output_file)


if __name__ == "__main__":
    main()
