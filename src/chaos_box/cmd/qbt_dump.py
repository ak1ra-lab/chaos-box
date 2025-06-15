# PYTHON_ARGCOMPLETE_OK

import argparse
import json
from pathlib import Path
from typing import Dict, List

import argcomplete
from fastbencode import bdecode

from chaos_box.logging import setup_logger

logger = setup_logger(__name__)


def decode_torrent_data_files(torrent_data: dict):
    info = torrent_data.get(b"info", {})
    files = info.get(b"files")
    if files is not None:
        # 多文件种子
        return [
            {
                "length": file[b"length"],
                "path": "/".join([p.decode() for p in file[b"path"]]),
            }
            for file in files
        ]
    else:
        # 单文件种子
        return [
            {
                "length": info.get(b"length"),
                "path": info.get(b"name", b"").decode() if b"name" in info else "",
            }
        ]


def bytes_to_str(obj: Dict | List | bytes) -> Dict | List | str:
    if isinstance(obj, dict):
        return {bytes_to_str(k): bytes_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [bytes_to_str(i) for i in obj]
    elif isinstance(obj, bytes):
        try:
            return obj.decode()
        except Exception:
            return str(obj)
    else:
        return obj


def torrent_dump(torrent_data: dict, file_path: Path):
    info = torrent_data.get(b"info", {})
    info.pop(b"pieces", None)
    files = decode_torrent_data_files(torrent_data)
    info_dict = bytes_to_str(info)
    info_dict["files"] = files
    output = {
        "name": file_path.name,
        "info": info_dict,
        "announce": bytes_to_str(torrent_data.get(b"announce", b"")),
    }
    logger.info("\n%s", json.dumps(output, indent=2, ensure_ascii=False))


def fastresume_dump(fastresume_data: dict, file_path: Path):
    fastresume_data.pop(b"peers", None)
    fastresume_data.pop(b"pieces", None)
    output = {
        "name": file_path.name,
        "data": bytes_to_str(fastresume_data),
    }
    logger.info("\n%s", json.dumps(output, indent=2, ensure_ascii=False))


def qbt_dump(torrent_file: Path) -> None:
    try:
        with open(torrent_file, "rb") as f:
            torrent_data = bdecode(f.read())
        suffix = torrent_file.suffix.lower()
        if suffix == ".torrent":
            torrent_dump(torrent_data, torrent_file)
        elif suffix == ".fastresume":
            fastresume_dump(torrent_data, torrent_file)
        else:
            logger.warning("Unknown file type: %s", torrent_file)
    except Exception as e:
        logger.error("Failed to parse %s: %s", torrent_file, e)


def parse_args() -> argparse.Namespace:
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
