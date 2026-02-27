"""Tests for qbt_dump utility functions."""

from chaos_box.cmd.qbt_dump import bytes_to_str, decode_torrent_data_files

# ---------------------------------------------------------------------------
# bytes_to_str
# ---------------------------------------------------------------------------


def test_bytes_to_str_simple_bytes() -> None:
    assert bytes_to_str(b"hello") == "hello"


def test_bytes_to_str_empty_bytes() -> None:
    assert bytes_to_str(b"") == ""


def test_bytes_to_str_invalid_utf8() -> None:
    """Bytes that cannot be decoded should fall back to repr."""
    result = bytes_to_str(b"\xff\xfe")
    assert result == str(b"\xff\xfe")


def test_bytes_to_str_passthrough_int() -> None:
    assert bytes_to_str(42) == 42  # type: ignore[arg-type]


def test_bytes_to_str_passthrough_none() -> None:
    assert bytes_to_str(None) is None  # type: ignore[arg-type]


def test_bytes_to_str_flat_dict() -> None:
    assert bytes_to_str({b"key": b"value"}) == {"key": "value"}


def test_bytes_to_str_flat_list() -> None:
    assert bytes_to_str([b"a", b"b", b"c"]) == ["a", "b", "c"]


def test_bytes_to_str_nested_dict() -> None:
    data = {b"info": {b"name": b"test", b"length": 1024}}
    result = bytes_to_str(data)
    assert result == {"info": {"name": "test", "length": 1024}}


def test_bytes_to_str_nested_list_in_dict() -> None:
    data = {b"announce-list": [[b"http://tracker1"], [b"http://tracker2"]]}
    result = bytes_to_str(data)
    assert result == {"announce-list": [["http://tracker1"], ["http://tracker2"]]}


def test_bytes_to_str_mixed_keys() -> None:
    """Dict keys that are bytes should also be decoded."""
    data = {b"utf8": b"ok", b"num": 99}
    result = bytes_to_str(data)
    assert result == {"utf8": "ok", "num": 99}


# ---------------------------------------------------------------------------
# decode_torrent_data_files
# ---------------------------------------------------------------------------


def test_decode_single_file_torrent() -> None:
    torrent_data = {
        b"info": {
            b"length": 1024,
            b"name": b"myfile.txt",
        }
    }
    result = decode_torrent_data_files(torrent_data)
    assert result == [{"length": 1024, "path": "myfile.txt"}]


def test_decode_multi_file_torrent() -> None:
    torrent_data = {
        b"info": {
            b"files": [
                {b"length": 100, b"path": [b"subdir", b"file1.txt"]},
                {b"length": 200, b"path": [b"file2.txt"]},
            ]
        }
    }
    result = decode_torrent_data_files(torrent_data)
    assert result == [
        {"length": 100, "path": "subdir/file1.txt"},
        {"length": 200, "path": "file2.txt"},
    ]


def test_decode_single_file_no_name() -> None:
    """Single-file torrent without a name key should return empty path."""
    torrent_data = {b"info": {b"length": 512}}
    result = decode_torrent_data_files(torrent_data)
    assert result == [{"length": 512, "path": ""}]


def test_decode_empty_torrent_data() -> None:
    """Missing info key should return a record with None length and empty path."""
    result = decode_torrent_data_files({})
    assert result == [{"length": None, "path": ""}]


def test_decode_multi_file_single_entry() -> None:
    """A multi-file torrent with one file should still return a list."""
    torrent_data = {
        b"info": {
            b"files": [
                {b"length": 42, b"path": [b"only.bin"]},
            ]
        }
    }
    result = decode_torrent_data_files(torrent_data)
    assert len(result) == 1
    assert result[0]["path"] == "only.bin"
