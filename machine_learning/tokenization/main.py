"""Entry point for training the GPT tokenizer on a text file."""

import logging

from gpt_tokenizer.data_loader import DataLoader
from gpt_tokenizer.tokenizer import GPTTokenizer

logger = logging.getLogger(__name__)

_TEXT_FILE_PATH = "data/text_test.txt"
_NUM_ITERATIONS = 20


def main() -> None:
    """Load and clean the text, then train the tokenizer on its UTF-8 bytes."""
    logging.basicConfig(level=logging.INFO)

    data_loader = DataLoader(_TEXT_FILE_PATH)
    text = data_loader.load_text()
    cleaned_text = data_loader.clean_text(text)

    if not cleaned_text:
        logger.error("No text to tokenize.")
        return

    encoded_text = cleaned_text.encode("utf-8")
    tokens = list(encoded_text)

    tokenizer = GPTTokenizer(encoded_text=tokens, num_iterations=_NUM_ITERATIONS)
    new_tokens, _ = tokenizer.tokenize()

    original_length = len(tokens)
    compressed_length = len(new_tokens)
    compression_rate = original_length / compressed_length

    logger.info(f"len(tokens)={original_length}")
    logger.info(f"len(new_tokens)={compressed_length}")
    logger.info(f"Compression rate: {compression_rate:.2f}")


if __name__ == "__main__":
    main()
