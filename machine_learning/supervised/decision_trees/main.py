"""Entry point for the decision tree training pipeline."""

from src.dts.data_pipeline import DataPipeline


def main() -> None:
    """
    Execute the main data pipeline.

    Loads, preprocesses, and analyzes the specified dataset, preparing it
    for decision tree model training.
    """
    dataset_name: str = "iris"
    pipeline = DataPipeline(dataset_name)
    df = pipeline.run()

    print(df)


if __name__ == "__main__":
    main()
