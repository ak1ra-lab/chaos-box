"""Tests for ipmerge utility functions."""

import pytest
from netaddr import IPNetwork

from chaos_box.cmd.ipmerge import (
    digit_str_zfill,
    digit_to_binary,
    ip_network_to_binary,
    ip_network_zfill,
)

# ---------------------------------------------------------------------------
# digit_str_zfill
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "digit_str, group, expected",
    [
        # group=4 (IPv6 hex groups)
        ("f", 4, "000f"),
        ("ff", 4, "00ff"),
        ("fff", 4, "0fff"),
        ("ffff", 4, "ffff"),
        ("10000", 4, "0001 0000"),  # 5 digits → padded to 8, split into two groups of 4
        ("0", 4, "0000"),
        # group=8 (IPv4 binary octets)
        ("1", 8, "00000001"),
        ("11000000", 8, "11000000"),
        # group=3 (IPv4 decimal octets with zfill)
        ("1", 3, "001"),
        ("10", 3, "010"),
        ("192", 3, "192"),
    ],
)
def test_digit_str_zfill(digit_str: str, group: int, expected: str) -> None:
    assert digit_str_zfill(digit_str, group) == expected


# ---------------------------------------------------------------------------
# digit_to_binary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "digit_str, base, group, expected",
    [
        # IPv6 hex → binary groups of 4
        ("0", 16, 4, "0000"),
        ("f", 16, 4, "1111"),
        ("ff", 16, 4, "1111 1111"),
        ("c0", 16, 4, "1100 0000"),
        ("a8", 16, 4, "1010 1000"),
        # IPv4 decimal → binary groups of 8
        ("0", 10, 8, "00000000"),
        ("1", 10, 8, "00000001"),
        ("192", 10, 8, "11000000"),
        ("168", 10, 8, "10101000"),
        ("255", 10, 8, "11111111"),
        # Invalid input → returned as-is
        ("zz", 16, 4, "zz"),
        ("xyz", 10, 8, "xyz"),
    ],
)
def test_digit_to_binary(digit_str: str, base: int, group: int, expected: str) -> None:
    assert digit_to_binary(digit_str, base, group) == expected


# ---------------------------------------------------------------------------
# ip_network_to_binary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cidr, expected",
    [
        (
            "0.0.0.0/0",
            "00000000.00000000.00000000.00000000/0",
        ),
        (
            "10.0.0.0/8",
            "00001010.00000000.00000000.00000000/8",
        ),
        (
            "192.168.0.0/24",
            "11000000.10101000.00000000.00000000/24",
        ),
        (
            "255.255.255.0/24",
            "11111111.11111111.11111111.00000000/24",
        ),
    ],
)
def test_ip_network_to_binary_ipv4(cidr: str, expected: str) -> None:
    assert ip_network_to_binary(IPNetwork(cidr)) == expected


def test_ip_network_to_binary_ipv6_compressed_passthrough() -> None:
    """netaddr uses compressed IPv6 notation; the function does not expand '::',
    so zero groups are passed through as empty strings rather than expanded to
    16-bit binary groups.  This test documents the current (limited) behaviour."""
    # "::" compressed notation stays compressed in the output
    assert ip_network_to_binary(IPNetwork("::/0")) == "::/0"
    # Only non-zero hextets before '::' are converted
    result = ip_network_to_binary(IPNetwork("2001:db8::/32"))
    assert result.startswith("0010 0000 0000 0001:")
    assert result.endswith("::/32")


# ---------------------------------------------------------------------------
# ip_network_zfill
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cidr, expected",
    [
        ("0.0.0.0/0", "000.000.000.000/0"),
        ("10.0.0.0/8", "010.000.000.000/8"),
        ("192.168.1.0/24", "192.168.001.000/24"),
        ("255.255.255.0/24", "255.255.255.000/24"),
    ],
)
def test_ip_network_zfill_ipv4(cidr: str, expected: str) -> None:
    assert ip_network_zfill(IPNetwork(cidr)) == expected
