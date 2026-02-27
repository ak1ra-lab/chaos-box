"""Tests for prime.is_prime()."""

import pytest

from chaos_box.cmd.prime import is_prime

# ---------------------------------------------------------------------------
# is_prime — parametrized unit tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "n, expected",
    [
        # Edge cases
        (-1, False),
        (0, False),
        (1, False),
        # Smallest primes
        (2, True),
        (3, True),
        (5, True),
        (7, True),
        # Small composites
        (4, False),
        (6, False),
        (8, False),
        (9, False),
        (10, False),
        # Larger primes
        (11, True),
        (13, True),
        (17, True),
        (19, True),
        (23, True),
        (97, True),
        (101, True),
        # Larger composites
        (100, False),
        (121, False),  # 11 * 11
        (1000, False),
        # Mersenne prime
        (8191, True),  # 2^13 − 1
        # Large composite
        (8189, False),  # 8189 = 53 * 1 * ... (not prime)
    ],
)
def test_is_prime(n: int, expected: bool) -> None:
    assert is_prime(n) is expected


def test_primes_below_30() -> None:
    known = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29}
    result = {n for n in range(30) if is_prime(n)}
    assert result == known
