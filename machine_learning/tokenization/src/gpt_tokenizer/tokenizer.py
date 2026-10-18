"""Module for the byte pair encoding (BPE) tokenizer."""

import logging
from collections import defaultdict
from itertools import pairwise

logger = logging.getLogger(__name__)

_NUM_BYTE_VALUES: int = 256


class GPTTokenizer:
    """Implement a simple Byte Pair Encoding (BPE) tokenizer.

    This tokenizer iteratively replaces the most frequent adjacent byte pairs
    with new byte values to form a more compact representation of the text.

    Attributes:
        encoded_text (list[int]): The current sequence of byte values.
        num_iterations (int): The number of byte pair merges to perform.
        replace_byte_value (int): The next unused byte value for a new merge.
        merges (dict[tuple[int, int], int]): Merged byte pairs and the byte
            value each one was replaced with.

    Example:
        >>> tokenizer = GPTTokenizer(encoded_text=[1, 2, 1, 2, 3], num_iterations=1)
        >>> new_tokens, merges = tokenizer.tokenize()
        >>> new_tokens
        [256, 256, 3]
    """

    def __init__(
        self,
        encoded_text: list[int],
        num_iterations: int,
    ) -> None:
        """Initialize the tokenizer with encoded text and iteration count.

        Args:
            encoded_text (list[int]): A list of integers representing encoded
                text.
            num_iterations (int): The number of iterations for byte pair
                merging.
        """
        self.encoded_text = encoded_text
        self.num_iterations = num_iterations
        self.replace_byte_value = _NUM_BYTE_VALUES
        self.merges: dict[tuple[int, int], int] = {}

    def find_top_pair(self) -> tuple[int, int]:
        """Find the most frequently occurring adjacent byte pair.

        Returns:
            top_pair (tuple[int, int]): The most frequent byte pair, or (0, 0)
                if the text has fewer than two values.
        """
        byte_pair_count: defaultdict[tuple[int, int], int] = defaultdict(int)

        for byte_pair in pairwise(self.encoded_text):
            byte_pair_count[byte_pair] += 1

        top_pair = max(
            byte_pair_count,
            key=lambda pair: byte_pair_count[pair],
            default=(0, 0),
        )

        return top_pair

    def merge_top_pair(self, top_pair: tuple[int, int]) -> None:
        """Replace occurrences of a byte pair in the encoded text.

        Scans the encoded text for consecutive occurrences of `top_pair` and
        replaces each one with `self.replace_byte_value`. The result is stored
        in `self.encoded_text`.

        Args:
            top_pair (tuple[int, int]): The byte pair to be merged.
        """
        i = 0
        new_bytes: list[int] = []

        while i < len(self.encoded_text):
            is_top_pair = i < len(self.encoded_text) - 1 and (
                self.encoded_text[i] == top_pair[0]
                and self.encoded_text[i + 1] == top_pair[1]
            )

            if is_top_pair:
                new_bytes.append(self.replace_byte_value)
                i += 2
            else:
                new_bytes.append(self.encoded_text[i])
                i += 1

        self.encoded_text = new_bytes

    def tokenize(self) -> tuple[list[int], dict[tuple[int, int], int]]:
        """Perform byte pair encoding for a fixed number of iterations.

        Iteratively finds and replaces the most frequent byte pairs in the
        encoded text, assigning new byte values sequentially. Each merge is
        logged.

        Returns:
            result (tuple[list[int], dict[tuple[int, int], int]]): The final
                encoded text, and the merges that produced it.
        """
        last_iteration = self.num_iterations - 1
        last_token = self.num_iterations + self.replace_byte_value - 1
        iteration_digits = len(str(last_iteration))
        token_digits = len(str(last_token))

        for i in range(self.num_iterations):
            top_pair = self.find_top_pair()

            logger.info(
                f"i={i:0{iteration_digits}}: Merging "
                f"({top_pair[0]:{token_digits}}, {top_pair[1]:{token_digits}}) "
                f"into a new token {self.replace_byte_value}"
            )
            self.merges[top_pair] = self.replace_byte_value

            self.merge_top_pair(top_pair=top_pair)
            self.replace_byte_value += 1

        result = (self.encoded_text, self.merges)

        return result
