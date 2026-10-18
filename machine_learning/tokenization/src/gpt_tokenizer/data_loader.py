"""Module for loading and cleaning text from a file."""

import logging
import re

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and clean text from a file.

    Attributes:
        file_path (str): Path to the text file.

    Example:
        >>> data_loader = DataLoader("data/text_test.txt")
        >>> text = data_loader.load_text()
        >>> cleaned_text = data_loader.clean_text(text)
    """

    def __init__(self, file_path: str) -> None:
        """Initialize the DataLoader with a file path.

        Args:
            file_path (str): The path to the text file.
        """
        self.file_path = file_path

    def load_text(self) -> str:
        """Load text from the specified file.

        Logs an error and returns an empty string if the file cannot be read.

        Returns:
            text (str): The contents of the file, or an empty string if an error
                occurs.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                text = file.read()
        except FileNotFoundError:
            logger.error(f"File '{self.file_path}' not found.")
            text = ""
        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Error: {e}")
            text = ""

        return text

    def clean_text(self, text: str) -> str:
        """Clean the given text by removing extra spaces and newlines.

        Args:
            text (str): The input text to be cleaned.

        Returns:
            cleaned_text (str): The text with excess spaces and newlines
                removed.
        """
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\n{2,}", "\n", text)
        cleaned_text = text.strip()

        return cleaned_text
