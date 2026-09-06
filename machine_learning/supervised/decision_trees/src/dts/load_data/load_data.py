"""Module for loading datasources."""

from pathlib import Path

import polars as pl
from polars import DataFrame

from src.dts.load_data.utils import load_yaml

_DATASET_CONFIG_FILE_PATH = Path("src/dts/load_data/dataset_configs.yaml")
_DATASET_CONFIG: dict = load_yaml(_DATASET_CONFIG_FILE_PATH)


def get_dataset_config(dataset: str) -> dict:
    """Retrieve the configuration for a given dataset name.

    Args:
        dataset (str): The dataset identifier.

    Returns:
        config (dict): The configuration dict containing url and read
            parameters.

    Raises:
        ValueError: If the dataset is not found.
    """
    if dataset not in _DATASET_CONFIG:
        raise ValueError(
            f"Unknown dataset: {dataset}. Available: {list(_DATASET_CONFIG.keys())}"
        )

    return _DATASET_CONFIG[dataset]


def load_data(dataset: str) -> DataFrame:
    """Load a dataset from UCI by name and return as Polars DataFrame.

    Args:
        dataset (str): The dataset identifier (e.g., 'iris', 'wine').

    Returns:
        df (DataFrame): The loaded dataset as a Polars DataFrame.

    Raises:
        ValueError: If the dataset is not found.
    """
    dataset_config = get_dataset_config(dataset)

    all_columns = dataset_config["features"] + [dataset_config["target"]]

    df = pl.read_csv(
        dataset_config["url"],
        has_header=dataset_config["has_header"],
        new_columns=all_columns,
    )

    return df
