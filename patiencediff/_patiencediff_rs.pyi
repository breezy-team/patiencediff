"""Type stubs for the Rust implementation of patiencediff."""

import difflib
from typing import Any, Callable, Literal, Sequence

class PatienceSequenceMatcher_rs(difflib.SequenceMatcher):
    """Python wrapper for patiencediff SequenceMatcher implemented in Rust.

    This class has a similar interface to difflib.SequenceMatcher but uses
    the patience diff algorithm for finding matching blocks.
    """

    def __init__(
        self,
        junk: Callable[[Any], bool] | None,
        a: Sequence[Any],
        b: Sequence[Any],
    ) -> None:
        """Initialize the SequenceMatcher.

        Args:
            junk: A function that determines if an element is junk (currently ignored).
            a: The first sequence to compare.
            b: The second sequence to compare.

        Raises:
            TypeError: If the sequences contain unhashable types.
        """
        ...

    def get_matching_blocks(self) -> list[difflib.Match]:
        """Return list of triples describing matching subsequences.

        Each triple is of the form (i, j, n), and means that
        a[i:i+n] == b[j:j+n]. The triples are monotonically increasing in
        i and in j.

        The last triple is a dummy, (len(a), len(b), 0), and is the only
        triple with n==0.

        Returns:
            List of (i, j, n) tuples describing matching blocks.
        """
        ...

    def get_opcodes(
        self,
    ) -> list[
        tuple[
            Literal["replace", "delete", "insert", "equal"], int, int, int, int
        ]
    ]:
        """Return list of 5-tuples describing how to turn a into b.

        Each tuple is of the form (tag, i1, i2, j1, j2). The first tuple
        has i1 == j1 == 0, and remaining tuples have i1 == the i2 from the
        tuple preceding it, and likewise for j1 == the previous j2.

        The tags are strings, with these meanings:
        - 'replace': a[i1:i2] should be replaced by b[j1:j2]
        - 'delete': a[i1:i2] should be deleted. Note that j1==j2 in this case.
        - 'insert': b[j1:j2] should be inserted at a[i1:i1]. Note that i1==i2 in this case.
        - 'equal': a[i1:i2] == b[j1:j2]

        Returns:
            List of (tag, i1, i2, j1, j2) tuples.
        """
        ...

    def get_grouped_opcodes(  # type: ignore[override]
        self, n: int = 3
    ) -> list[
        list[
            tuple[
                Literal["replace", "delete", "insert", "equal"],
                int,
                int,
                int,
                int,
            ]
        ]
    ]:
        """Return a list of groups with up to n lines of context.

        Each group is in the same format as returned by get_opcodes().

        Args:
            n: Number of lines of context to include (default: 3).

        Returns:
            List of groups, where each group is a list of opcodes.
        """
        ...

def unique_lcs_rs(a: Sequence[Any], b: Sequence[Any]) -> list[tuple[int, int]]:
    """Find the longest common subsequence of unique elements in sequences a and b.

    This only matches elements which are unique on both sides.
    This helps prevent common elements from over influencing match results.
    The longest common subset uses the Patience Sorting algorithm:
    http://en.wikipedia.org/wiki/Patience_sorting

    Args:
        a: An indexable sequence (such as a list of strings).
        b: Another indexable sequence (such as a list of strings).

    Returns:
        A list of tuples, one for each element which is matched.
        [(position_in_a, position_in_b), ...]
    """
    ...

def recurse_matches_rs(
    a: Sequence[Any],
    b: Sequence[Any],
    alo: int,
    blo: int,
    ahi: int,
    bhi: int,
    answer: list[tuple[int, int]],
    maxrecursion: int,
) -> None:
    """Recursively find matches between two sequences.

    This function uses the patience sorting algorithm to find matching
    blocks between subsequences a[alo:ahi] and b[blo:bhi].

    Args:
        a: The first sequence.
        b: The second sequence.
        alo: Start index in sequence a.
        blo: Start index in sequence b.
        ahi: End index in sequence a.
        bhi: End index in sequence b.
        answer: List to append matches to (modified in place).
        maxrecursion: Maximum recursion depth allowed.
    """
    ...
