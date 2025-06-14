# PYTHON_ARGCOMPLETE_OK

import argparse
import re
from pathlib import Path

import argcomplete
from fastbencode import bdecode, bencode

from miscbox.logging import setup_logger

logger = setup_logger(__name__)


def qbt_migrate(
    file: Path,
    pattern: str,
    repl: str,
    auto_managed=0,
    private=0,
    apply=False,
):
    with open(file, "rb") as f:
        fastresume = bdecode(f.read())

    if auto_managed in (0, 1):
        if fastresume.get(b"auto_managed", 0) != auto_managed:
            return

    if private in (0, 1):
        with open(file.with_suffix(".torrent"), "rb") as f:
            torrent = bdecode(f.read())
        if torrent.get(b"info", {}).get(b"private", 0) != private:
            return

    name = fastresume.get(b"name", b"").decode()
    save_path = fastresume.get(b"save_path", b"").decode()
    qBt_category = fastresume.get(b"qBt-category", b"").decode()

    logger.info(
        "< name: %s, save_path: %s, qBt-category: %s", name, save_path, qBt_category
    )

    if not re.search(pattern, save_path):
        return

    save_path = re.sub(pattern, repl, save_path)
    qBt_category = re.sub(pattern, repl, qBt_category)

    logger.info(
        "> name: %s, save_path: %s, qBt-category: %s\n", name, save_path, qBt_category
    )

    if apply:
        fastresume[b"save_path"] = save_path.encode()
        fastresume[b"qBt-category"] = qBt_category.encode()

        with open(file, "wb") as f:
            f.write(bencode(fastresume))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--BT_backup",
        default="./BT_backup",
        help="qBittorrent BT_backup directory, default: '%(default)s'",
    )
    parser.add_argument(
        "--pattern",
        default=r"main/",
        help="save_path re.search pattern for .fastresume files, default: '%(default)s'",
    )
    parser.add_argument(
        "--repl",
        default=r"tank/",
        help="save_path re.sub replacement for .fastresume files, default: '%(default)s'",
    )
    parser.add_argument(
        "--auto_managed",
        choices=(0, 1),
        default=2,
        type=int,
        help="filter auto_managed(1) or not(0) tasks",
    )
    parser.add_argument(
        "--private",
        choices=(0, 1),
        default=2,
        type=int,
        help="filter private(1) or public(0) tasks",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the renaming (default is dry-run)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main():
    args = parse_args()
    BT_backup = Path(args.BT_backup).resolve()
    if not BT_backup.exists():
        logger.warning("BT_backup: %s does not exists", BT_backup)
        return

    for file in BT_backup.rglob("*.fastresume"):
        qbt_migrate(
            file, args.pattern, args.repl, args.auto_managed, args.private, args.apply
        )


if __name__ == "__main__":
    main()
