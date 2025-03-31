from collections import Counter
from itertools import combinations, permutations


def non_repeating_character(string):
    """
    Given a string, returns the first non-repeating character. If none exists, returns an empty string.
    Character comparisons are case-insensitive, but the returned character should preserve its original case.

    Examples:
        string = 'submission' -> returns 'u'
        string = 'nnn' -> returns ''
        string = 'SUbMission' -> returns 'U'

    Args:
        string: The input string to analyze.

    Returns:
        The first non-repeating character or an empty string if none exists.
    """
    if not string:
        return ""

    # Maps lowercase characters to their original case
    char_map = {char.lower(): char for char in string}

    # Counts occurrences of each character (case-insensitive)
    counter = Counter(string.lower())

    # Finds the first non-repeating character
    for char in string.lower():
        if counter[char] == 1:
            return char_map[char]

    return ""


def multiples_of_3(num):
    """
    Given an integer (num), returns a list containing two values:
    - The total count of unique numbers divisible by 3, formed from combinations of num's digits.
    - The maximum number among those combinations that is divisible by 3.

    Notes:
        - 0 is excluded from the count.
        - Numbers must be formed using the digits of `num`, and combinations may have different lengths.
        - If no valid number exists, return [0, None].

    Examples:
        num = 39 -> returns [4, 93] (Valid numbers: 3, 9, 39, 93)
        num = 330 -> returns [5, 330] (Valid numbers: 3, 30, 33, 303, 330)
        num = 23 -> returns [1, 3] (Valid numbers: 2, 3, 23, 32; only 3 is valid)

    Args:
        num: The integer to analyze.

    Returns:
        A list containing the count of multiples of 3 and the highest multiple of 3.
    """
    num_str = str(num)
    all_combinations = set()

    # Generate all possible number combinations of different lengths
    for length in range(1, len(num_str) + 1):
        for combo in combinations(num_str, length):
            for perm in permutations(combo):
                num_comb = int("".join(perm))
                if num_comb > 0:  # Exclude zero
                    all_combinations.add(num_comb)

    # Filter numbers divisible by 3
    multiples = [n for n in all_combinations if n % 3 == 0]

    return [len(multiples), max(multiples) if multiples else None]