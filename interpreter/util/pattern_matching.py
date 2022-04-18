# -*- coding: utf-8 -*-
"""
This python module matches repeating patterns in a list of elements,
which can be used e.g. to remove repeating parts from recursive stack traces.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import DefaultDict
from typing import Dict
from typing import Hashable
from typing import List

DiffDict = Dict[Hashable, DefaultDict[int, List[int]]]


@dataclass
class Pattern:
    """Pattern class, contains data for a repeating pattern"""

    start_index: int = 0
    length: int = 0
    repetitions: int = 2
    valid: bool = field(default=True, repr=False)

    def check_matching_pattern(self, pattern: Pattern) -> bool:
        """Returns True if pattern lengths match and the pattern start index is in range."""
        return self.length == pattern.length and pattern.start_index in self.range

    def delay_start(self) -> None:
        """Decrements pattern repetitions by 1,
        and sets valid to False if less than 2 repetitions.
        """
        self.repetitions -= 1
        self.start_index += self.length
        if self.repetitions < 2:
            self.valid = False

    @property
    def range(self) -> range:
        """The index range covered by the repeating pattern"""
        return range(self.start_index, self.end)

    @property
    def end(self) -> int:
        """The index at which the repeating pattern stops"""
        return self.start_index + self.length * self.repetitions


def determine_distances_between_patterns(elements: List[Hashable]) -> DiffDict:
    """Returns a dict mapping of element to a mapping of {
        length between same element occurence:
        list of indices at starting indices at which element occured
    }.
    """
    indices: DefaultDict[Hashable, List[int]] = defaultdict(list)
    for i, element in enumerate(elements):
        indices[element].append(i)

    differences: DiffDict = {element: defaultdict(list) for element in elements}
    for element, pattern in indices.items():
        if len(pattern) < 2:
            continue

        for current, previous in zip(pattern[1:], pattern):
            diff = current - previous
            differences[element][diff].append(previous)
    return differences


def determine_patterns_in_distances(differences: DiffDict) -> Dict[int, Pattern]:
    """Returns a dictionary of starting index to a spotted repetition pattern from the
    differences dict passed.

    See determine_distances_between_elements for differences doc.
    """
    spotted_patterns: Dict[int, Pattern] = {}
    for differences_ in differences.values():
        if not differences_:
            continue

        for diff, start_indices in differences_.items():
            current_pattern = Pattern(length=0, repetitions=0)
            for start_index in start_indices:
                new_pattern = Pattern(start_index, length=diff)
                if current_pattern.check_matching_pattern(new_pattern):
                    current_pattern.repetitions += 1
                    continue

                if current_pattern.repetitions > 1:
                    spotted_patterns[current_pattern.start_index] = current_pattern
                current_pattern = new_pattern

            if current_pattern.repetitions > 1:
                spotted_patterns[current_pattern.start_index] = current_pattern
    return spotted_patterns


def _determine_valid_patterns(spotted_patterns: Dict[int, Pattern]) -> List[Pattern]:
    """Filters out invalid patterns and duplicates"""
    for pattern in sorted(spotted_patterns.values(), key=lambda x: x.start_index):
        _check_validity(pattern, spotted_patterns)
    patterns = [pattern for pattern in spotted_patterns.values() if pattern.valid]
    return patterns


def _check_validity(pattern: Pattern, spotted_patterns: Dict[int, Pattern]):
    """Recursively filters out invalid and duplicate patterns. When patterns could match,
    but don't because of their respective starting indices, it tries to start matching the
    earliest pattern from a later point.
    """
    if pattern.repetitions < 2 or not pattern.valid:
        pattern.valid = False
        return

    start = pattern.start_index + 1
    end = pattern.start_index + pattern.length
    for i in range(start, end):
        matching_pattern = spotted_patterns.get(i)

        # patterns dont necessarily match at each others first starting index
        # e.g. [6, 8, 6, 7, 6, 7] has the 6 pattern start at 0 and the 7 pattern start at 4
        if matching_pattern is None:
            pattern.delay_start()
            _check_validity(pattern, spotted_patterns)
            continue

        if matching_pattern.length != pattern.length:
            pattern.valid = False
            return

        pattern.repetitions = min(pattern.repetitions, matching_pattern.repetitions)


def determine_patterns(elements: List[Hashable]) -> List[Pattern]:
    """Returns a list of Pattern objects determined from repeating patterns
    in the specified elements.
    """
    distances = determine_distances_between_patterns(elements)
    patterns = determine_patterns_in_distances(distances)
    valid_patterns = _determine_valid_patterns(patterns)
    return valid_patterns


if __name__ == "__main__":
    print(
        determine_patterns(
            elements=[
                0,
                1,
                2,
                3,
                4,
                2,
                3,
                4,
                2,
                3,
                4,
                5,
                6,
                8,
                6,
                7,
                6,
                7,
                2,
                3,
                4,
                2,
                3,
                4,
            ]
        )
    )
