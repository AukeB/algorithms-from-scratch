"""Module for loading datasources."""

from pathlib import Path
from typing import TypedDict

import polars as pl
from polars import DataFrame

from dts.load_data.utils import load_yaml

_DATASET_CONFIG_FILE_PATH = Path(__file__).parent / "dataset_configs.yaml"


class DatasetConfig(TypedDict):
    """Configuration of one dataset, as listed in dataset_configs.yaml.

    Attributes:
        url (str): Where the dataset is downloaded from.
        has_header (bool): Whether the first row of the file is a header.
        features (list[str]): Names of the feature columns, in file order.
        target (str): Name of the target column.
    """

    url: str
    has_header: bool
    features: list[str]
    target: str


_DATASET_CONFIG: dict[str, DatasetConfig] = load_yaml(_DATASET_CONFIG_FILE_PATH)


def get_dataset_config(dataset: str) -> DatasetConfig:
    """Retrieve the configuration for a given dataset name.

    Args:
        dataset (str): The dataset identifier.

    Returns:
        dataset_config (DatasetConfig): The url, header flag, features and
            target of the dataset.

    Raises:
        ValueError: If the dataset is not found.
    """
    if dataset not in _DATASET_CONFIG:
        available_datasets = list(_DATASET_CONFIG.keys())
        raise ValueError(f"Unknown dataset: {dataset}. Available: {available_datasets}")

    dataset_config = _DATASET_CONFIG[dataset]

    return dataset_config


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
