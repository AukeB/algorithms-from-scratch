"""Entry point for the decision tree training pipeline."""

import logging

from dts.data_pipeline import DataPipeline

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Execute the main data pipeline.

    Loads, preprocesses, and analyzes the specified dataset, preparing it
    for decision tree model training.
    """
    logging.basicConfig(level=logging.INFO)

    dataset_name: str = "iris"
    pipeline = DataPipeline(dataset_name)
    df = pipeline.run()

    logger.info(f"Preprocessed dataset:\n{df}")


if __name__ == "__main__":
    main()
