# PYTHON_ARGCOMPLETE_OK

import argparse
import json

import argcomplete
from chaos_utils.text_utils import save_json


def sort_keys(filenames: list) -> None:
    for filename in filenames:
        with open(filename) as f:
            data = json.loads(f.read())
        save_json(filename, data)


def main():
    parser = argparse.ArgumentParser(
        description="read .json files then save it with sort_keys"
    )
    parser.add_argument(
        "filenames",
        nargs="+",
        metavar="JSON_FILE",
        help=".json filenames",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    sort_keys(args.filenames)


if __name__ == "__main__":
    main()
