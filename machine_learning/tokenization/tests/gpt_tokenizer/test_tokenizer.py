"""Tests for the tokenizer module."""

import logging

import pytest

from gpt_tokenizer.tokenizer import GPTTokenizer


# Testing the "__init__" method from the "GPTTokenizer" class.


def test_init_starts_with_first_new_byte_value_and_no_merges() -> None:
    tokenizer = GPTTokenizer(encoded_text=[1, 2, 3], num_iterations=2)

    assert tokenizer.replace_byte_value == 256
    assert tokenizer.merges == {}


# Testing the "find_top_pair" method from the "GPTTokenizer" class.


def test_find_top_pair_returns_most_frequent_pair() -> None:
    tokenizer = GPTTokenizer(encoded_text=[1, 2, 1, 2, 3], num_iterations=1)

    top_pair = tokenizer.find_top_pair()

    assert top_pair == (1, 2)


def test_find_top_pair_returns_default_for_single_value() -> None:
    tokenizer = GPTTokenizer(encoded_text=[7], num_iterations=1)

    top_pair = tokenizer.find_top_pair()

    assert top_pair == (0, 0)


# Testing the "merge_top_pair" method from the "GPTTokenizer" class.


def test_merge_top_pair_replaces_every_occurrence() -> None:
    tokenizer = GPTTokenizer(encoded_text=[5, 6, 6, 7, 9, 1], num_iterations=1)
    tokenizer.replace_byte_value = 99

    tokenizer.merge_top_pair(top_pair=(6, 7))

    assert tokenizer.encoded_text == [5, 6, 99, 9, 1]


def test_merge_top_pair_keeps_trailing_value_that_is_not_a_pair() -> None:
    tokenizer = GPTTokenizer(encoded_text=[1, 2, 3], num_iterations=1)

    tokenizer.merge_top_pair(top_pair=(2, 3))

    assert tokenizer.encoded_text == [1, 256]


# Testing the "tokenize" method from the "GPTTokenizer" class.


def test_tokenize_merges_pairs_and_records_them(caplog: pytest.LogCaptureFixture) -> None:
    tokenizer = GPTTokenizer(encoded_text=[1, 2, 1, 2, 3], num_iterations=1)

    with caplog.at_level(logging.INFO, logger="gpt_tokenizer.tokenizer"):
        new_tokens, merges = tokenizer.tokenize()

    assert new_tokens == [256, 256, 3]
    assert merges == {(1, 2): 256}
    assert "Merging" in caplog.text


def test_tokenize_assigns_sequential_byte_values() -> None:
    tokenizer = GPTTokenizer(encoded_text=[1, 2, 1, 2, 3], num_iterations=2)

    new_tokens, merges = tokenizer.tokenize()

    assert merges == {(1, 2): 256, (256, 256): 257}
    assert max(new_tokens) == 256 + 2 - 1
