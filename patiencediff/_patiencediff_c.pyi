import difflib
from typing import Any, Sequence

class PatienceSequenceMatcher_c(difflib.SequenceMatcher):

    def get_matching_blocks(self) -> list[difflib.Match]: ...


def unique_lcs_c(a: Sequence[Any], b: Sequence[Any]) -> list[tuple[int, int]]: ...


def recurse_matches_c(
        a: Sequence[Any], b: Sequence[Any],
        alo: int, blo: int, ahi: int, bhi: int,
        answer: list[tuple[int, int]], maxrecursion: int) -> None: ...

