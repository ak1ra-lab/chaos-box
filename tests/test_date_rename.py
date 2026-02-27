"""Tests for date_rename.get_dest_filename()."""

import os
from datetime import datetime
from pathlib import Path

from chaos_box.cmd.date_rename import get_dest_filename


def _set_mtime(path: Path, dt: datetime) -> None:
    """Set a file's mtime to the given datetime (local time)."""
    ts = dt.timestamp()
    os.utime(path, (ts, ts))


FIXED_DATE = datetime(2024, 1, 15)
FIXED_PREFIX = "2024-01-15"


# ---------------------------------------------------------------------------
# get_dest_filename
# ---------------------------------------------------------------------------


def test_no_prefix_gets_date_prefixed(tmp_path: Path) -> None:
    """A file without a date prefix should get one from its mtime."""
    f = tmp_path / "myfile.txt"
    f.touch()
    _set_mtime(f, FIXED_DATE)

    dest, should_rename = get_dest_filename(f)

    assert dest.name == f"{FIXED_PREFIX}-myfile.txt"
    assert should_rename is True


def test_already_correct_prefix_no_rename(tmp_path: Path) -> None:
    """A file already named with the correct date prefix should not be renamed."""
    f = tmp_path / f"{FIXED_PREFIX}-myfile.txt"
    f.touch()
    _set_mtime(f, FIXED_DATE)

    dest, should_rename = get_dest_filename(f)

    assert dest == f
    assert should_rename is False


def test_old_date_prefix_gets_updated(tmp_path: Path) -> None:
    """A file with a stale date prefix should have its prefix updated."""
    f = tmp_path / "2020-03-22-myfile.txt"
    f.touch()
    _set_mtime(f, FIXED_DATE)

    dest, should_rename = get_dest_filename(f)

    assert dest.name == f"{FIXED_PREFIX}-myfile.txt"
    assert should_rename is True


def test_two_digit_prefix_gets_replaced(tmp_path: Path) -> None:
    """A file with a NN- prefix (matched by regex) should have it replaced."""
    f = tmp_path / "25-myfile.txt"
    f.touch()
    _set_mtime(f, FIXED_DATE)

    dest, should_rename = get_dest_filename(f)

    assert dest.name == f"{FIXED_PREFIX}-myfile.txt"
    assert should_rename is True


def test_dest_path_is_sibling(tmp_path: Path) -> None:
    """The destination path should be in the same directory as the source."""
    f = tmp_path / "report.pdf"
    f.touch()
    _set_mtime(f, FIXED_DATE)

    dest, _ = get_dest_filename(f)

    assert dest.parent == tmp_path


def test_no_extension(tmp_path: Path) -> None:
    """Files without an extension should also get prefixed correctly."""
    f = tmp_path / "README"
    f.touch()
    _set_mtime(f, FIXED_DATE)

    dest, should_rename = get_dest_filename(f)

    assert dest.name == f"{FIXED_PREFIX}-README"
    assert should_rename is True
