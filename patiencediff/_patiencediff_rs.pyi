import difflib
from typing import Any, Callable, Literal, Sequence, TypeVar

T = TypeVar("T")

class PatienceSequenceMatcher_rs(difflib.SequenceMatcher):
    def __init__(
        self, junk: Callable[[T], bool] | None, a: Sequence[T], b: Sequence[T]
    ) -> None: ...
    def get_matching_blocks(self) -> list[difflib.Match]: ...
    def get_opcodes(
        self,
    ) -> list[
        tuple[
            Literal["replace", "delete", "insert", "equal"], int, int, int, int
        ]
    ]: ...
    def get_grouped_opcodes(
        self, n: int = 3
    ) -> list[list[tuple[str, int, int, int, int]]]: ...

def unique_lcs_rs(
    a: Sequence[Any], b: Sequence[Any]
) -> list[tuple[int, int]]: ...
def recurse_matches_rs(
    a: Sequence[Any],
    b: Sequence[Any],
    alo: int,
    blo: int,
    ahi: int,
    bhi: int,
    answer: list[tuple[int, int]],
    maxrecursion: int,
) -> None: ...
