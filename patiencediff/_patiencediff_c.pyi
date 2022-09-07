import difflib
from typing import List, Tuple, Sequence, Any


class PatienceSequenceMatcher_c(difflib.SequenceMatcher):

    def get_matching_blocks(self) -> List[difflib.Match]: ...


def unique_lcs_c(a: Sequence[Any], b: Sequence[Any]) -> List[Tuple[int, int]]: ...


def recurse_matches_c(
        a: Sequence[Any], b: Sequence[Any],
        alo: int, blo: int, ahi: int, bhi: int,
        answer: List[Tuple[int, int]], maxrecursion: int) -> None: ...

