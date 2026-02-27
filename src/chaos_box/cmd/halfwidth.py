"""Convert full-width punctuation to half-width in text files."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import sys
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)

KEYMAPS = {
    "。": ".",
    "，": ",",
    "：": ":",
    "；": ";",
    "、": ",",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "｛": "{",
    "｝": "}",
    "「": "{",
    "」": "}",
    "『": "{",
    "』": "}",
    "《": "<",
    "》": ">",
    "·": "`",
    "…": "^",
    "￥": "$",
    "¥": "$",
    "？": "?",
    "！": "!",
    "—": "_",
    "｜": "|",
}

PUNCTUATIONS_NEED_SPACE = set(".:,;!?")
PUNCTUATIONS_NEXT_CHAR_EXCEPTIONS = set(" \n\r\t.,，。：；？！、")

# Half-width brackets that need surrounding spaces when mid-sentence
BRACKETS_OPEN = set("([{")
BRACKETS_CLOSE = set(")]}")
# Don't add a leading space before an open bracket when preceded by these chars
BRACKETS_OPEN_PREV_CHAR_EXCEPTIONS = set(" \n\r\t([{")


def convert_line(line: str) -> str:
    """Convert punctuation in a line of text.

    Args:
        line: Input text line

    Returns:
        Text with converted punctuation
    """
    new_line = ""
    for i, ch in enumerate(line):
        if ch not in KEYMAPS:
            new_line += ch
            continue

        half = KEYMAPS[ch]
        is_line_end = i == len(line.strip()) - 1
        next_char = line[i + 1] if i + 1 < len(line) else ""
        prev_char = new_line[-1] if new_line else ""

        # Opening bracket mid-sentence: insert a space before it
        if (
            half in BRACKETS_OPEN
            and prev_char
            and prev_char not in BRACKETS_OPEN_PREV_CHAR_EXCEPTIONS
        ):
            new_line += " "

        new_line += half

        # Closing bracket: add space after, unless at line end or followed by punctuation/space
        if half in BRACKETS_CLOSE:
            if not is_line_end and next_char not in PUNCTUATIONS_NEXT_CHAR_EXCEPTIONS:
                new_line += " "
        elif (
            half in PUNCTUATIONS_NEED_SPACE
            and not is_line_end
            and next_char not in PUNCTUATIONS_NEXT_CHAR_EXCEPTIONS
        ):
            new_line += " "

    return new_line


def process_file(filepath: Path, inplace: bool) -> None:
    """Process a single file.

    Args:
        filepath: Path to file to process
        inplace: If True, modify file in place
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    converted_lines = [convert_line(line) for line in lines]

    if inplace:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(converted_lines)
    else:
        for line in converted_lines:
            print(line, end="")


def main() -> None:
    """Parse arguments and convert full-width punctuation in files."""
    parser = argparse.ArgumentParser(
        description="Convert full-width punctuation to half-width in text files."
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="Input text files")
    parser.add_argument(
        "-i", "--inplace", action="store_true", help="Edit the file in place"
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    for file in args.files:
        filepath = Path(file)
        if not filepath.exists():
            logger.error("File not found: %s", filepath)
            sys.exit(1)

        process_file(filepath, args.inplace)


if __name__ == "__main__":
    main()
