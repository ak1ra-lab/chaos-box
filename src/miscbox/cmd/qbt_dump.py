# PYTHON_ARGCOMPLETE_OK

import argparse
from pathlib import Path

import argcomplete
from fastbencode import bdecode

from miscbox.logging import setup_logger

logger = setup_logger(__name__)


def decode_torrent_data_files(torrent_data: dict):
    try:
        torrent_data_files_bytes_list = torrent_data[b"info"][b"files"]
    except KeyError:
        name = torrent_data[b"info"][b"name"]
        logger.warning("KeyError: torrent %s has no files", name)
        return []

    torrent_data_files = []
    for file in torrent_data_files_bytes_list:
        torrent_data_files.append(
            {
                "length": file[b"length"],
                "path": "/".join([p.decode() for p in file[b"path"]]),
            }
        )

    return torrent_data_files


def torrent_dump(torrent_data: dict):
    torrent_data_files = decode_torrent_data_files(torrent_data)
    torrent_data[b"info"][b"files"] = torrent_data_files

    logger.info(torrent_data)


def fastresume_dump(fastresume_data: dict):
    logger.info(fastresume_data)


def qbt_dump(torrent_file: Path):
    with open(torrent_file, "rb") as f:
        torrent_data = bdecode(f.read())

    if torrent_file.suffix == ".torrent":
        torrent_dump(torrent_data)
    elif torrent_file.suffix == ".fastresume":
        fastresume_dump(torrent_data)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "torrents",
        nargs="+",
        metavar="TORRENT",
        help="bencoded torrent files to dump",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main():
    args = parse_args()

    for torrent in args.torrents:
        qbt_dump(Path(torrent))


if __name__ == "__main__":
    main()
