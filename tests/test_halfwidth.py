"""Tests for halfwidth.convert_line() and process_file()."""

import pytest

from chaos_box.cmd.halfwidth import convert_line, process_file

# ---------------------------------------------------------------------------
# convert_line — parametrized unit tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line, expected",
    [
        # No full-width chars → unchanged
        ("Hello world", "Hello world"),
        ("", ""),
        # Basic punctuation at line end → no trailing space
        ("你好。", "你好."),
        ("你好！", "你好!"),
        ("你好？", "你好?"),
        ("你好，", "你好,"),
        # Punctuation in the middle → space appended
        ("你好，世界", "你好, 世界"),
        ("你好！世界", "你好! 世界"),
        ("你好？世界", "你好? 世界"),
        ("你好：世界", "你好: 世界"),
        ("你好；世界", "你好; 世界"),
        # Next char is already a space → no double-space
        ("你好， 世界", "你好, 世界"),
        ("你好！ 世界", "你好! 世界"),
        # Next char is a full-width exception (，。：；？！、) → no space
        ("你好，，世界", "你好,, 世界"),
        ("你好，。世界", "你好,. 世界"),
        # Quotes map directly (not in PUNCTUATIONS_NEED_SPACE, not in brackets sets)
        # Use unicode escapes to avoid Python parser treating curly quotes as delimiters
        ("\u201c你好\u201d", '"你好"'),
        ("\u2018你好\u2019", "'你好'"),
        # Brackets alone (start / end of line) → no extra spaces
        ("（你好）", "(你好)"),
        ("【你好】", "[你好]"),
        # Brackets at LINE START followed by more text → space only AFTER closing bracket
        ("（你好）文字", "(你好) 文字"),
        ("【你好】文字", "[你好] 文字"),
        # Brackets in MIDDLE of sentence → space before open AND after close
        ("段落（括号）文字", "段落 (括号) 文字"),
        ("有【方括号】内容", "有 [方括号] 内容"),
        ("有「引用」文字", "有 {引用} 文字"),
        # Consecutive brackets → space between pairs
        ("（好）（坏）", "(好) (坏)"),
        # Bracket already preceded by a space → no double-space
        ("文字 （括号）", "文字 (括号)"),
        # Closing bracket followed by a comma/period → no space (comma/period are exceptions)
        ("（你好），下一句", "(你好), 下一句"),
        ("（你好）。下一句", "(你好). 下一句"),
        # Symbols → no space needed
        ("——", "----"),
        ("…", "..."),
        ("￥100", "￥100"),
        ("¥100", "¥100"),
        # Mixed ASCII and full-width
        ("price：100", "price: 100"),
        # Newline at end — is_line_end strips trailing whitespace
        ("你好，\n", "你好,\n"),
    ],
)
def test_convert_line(line: str, expected: str) -> None:
    assert convert_line(line) == expected


# ---------------------------------------------------------------------------
# process_file — file I/O tests using tmp_path
# ---------------------------------------------------------------------------


def test_process_file_stdout(tmp_path, capsys) -> None:
    """Non-inplace mode should print converted lines to stdout."""
    f = tmp_path / "test.txt"
    f.write_text("你好，世界。\n", encoding="utf-8")

    process_file(f, inplace=False)

    captured = capsys.readouterr()
    assert captured.out == "你好, 世界.\n"


def test_process_file_inplace(tmp_path) -> None:
    """Inplace mode should modify the file in place."""
    f = tmp_path / "test.txt"
    f.write_text("你好，世界。\n", encoding="utf-8")

    process_file(f, inplace=True)

    assert f.read_text(encoding="utf-8") == "你好, 世界.\n"


def test_process_file_inplace_multiline(tmp_path) -> None:
    """Inplace mode should convert all lines."""
    f = tmp_path / "multi.txt"
    f.write_text("第一行：内容\n第二行！结束\n", encoding="utf-8")

    process_file(f, inplace=True)

    lines = f.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "第一行: 内容"
    assert lines[1] == "第二行! 结束"


def test_process_file_no_fullwidth(tmp_path, capsys) -> None:
    """Files without full-width chars should be output unchanged."""
    content = "Hello, world!\n"
    f = tmp_path / "ascii.txt"
    f.write_text(content, encoding="utf-8")

    process_file(f, inplace=False)

    assert capsys.readouterr().out == content
