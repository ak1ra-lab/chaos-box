"""Tests for pascal.gen_next_row() and gen_pascal_triangle()."""

import pytest

from chaos_box.cmd.pascal import gen_next_row, gen_pascal_triangle

# ---------------------------------------------------------------------------
# gen_next_row
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prev_row, expected",
    [
        ([1], [1, 1]),
        ([1, 1], [1, 2, 1]),
        ([1, 2, 1], [1, 3, 3, 1]),
        ([1, 3, 3, 1], [1, 4, 6, 4, 1]),
        ([1, 4, 6, 4, 1], [1, 5, 10, 10, 5, 1]),
    ],
)
def test_gen_next_row(prev_row: list[int], expected: list[int]) -> None:
    assert gen_next_row(prev_row) == expected


def test_gen_next_row_preserves_symmetry() -> None:
    """Each generated row should be palindromic."""
    row = [1]
    for _ in range(10):
        row = gen_next_row(row)
        assert row == row[::-1]


# ---------------------------------------------------------------------------
# gen_pascal_triangle
# ---------------------------------------------------------------------------


def test_gen_pascal_triangle_zero_rows() -> None:
    assert gen_pascal_triangle(0) == []


def test_gen_pascal_triangle_one_row() -> None:
    assert gen_pascal_triangle(1) == [[1]]


@pytest.mark.parametrize(
    "num_rows, expected",
    [
        (2, [[1], [1, 1]]),
        (3, [[1], [1, 1], [1, 2, 1]]),
        (5, [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]),
    ],
)
def test_gen_pascal_triangle(num_rows: int, expected: list[list[int]]) -> None:
    assert gen_pascal_triangle(num_rows) == expected


def test_gen_pascal_triangle_row_lengths() -> None:
    """Row i (0-indexed) must have exactly i+1 elements."""
    triangle = gen_pascal_triangle(10)
    for i, row in enumerate(triangle):
        assert len(row) == i + 1


def test_gen_pascal_triangle_row_sums() -> None:
    """Sum of row i must equal 2**i."""
    triangle = gen_pascal_triangle(10)
    for i, row in enumerate(triangle):
        assert sum(row) == 2**i


def test_gen_pascal_triangle_symmetry() -> None:
    """Every row must be palindromic."""
    for row in gen_pascal_triangle(12):
        assert row == row[::-1]
