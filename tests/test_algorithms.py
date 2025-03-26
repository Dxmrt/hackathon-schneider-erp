from algorithms.functions import multiples_of_3, non_repeating_character


def test_non_repeating_character_1():
    char = non_repeating_character("submission")
    assert char == "u"


def test_non_repeating_character_2():
    char = non_repeating_character("asEREERdfasdfdasdASDFADDFG")
    assert char == "G"


def test_multiples_1():
    char = multiples_of_3(3)
    assert char == [1, 3]


def test_multiples_2():
    char = multiples_of_3(94471298)
    assert char == [5426, 9987441]
