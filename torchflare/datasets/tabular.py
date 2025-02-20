"""Implements datasets for task involving tabular data."""
from __future__ import annotations

from typing import List, Union

import pandas as pd
import torch
from torch.utils.data import Dataset


class TabularDataset(Dataset):
    """Class to create a dataset for tasks involving tabular data."""

    def __init__(self, inputs, labels=None):
        """Constructor for Tabular Dataset class.

        Args:
            inputs: A np.array of features.
            labels : A np.array of labels.
        """
        self.inputs = inputs
        self.labels = labels

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        feature_cols: Union[str, List[str]],
        label_cols: Union[str, List[str]] = None,
    ) -> TabularDataset:
        """Classmethod to create pytorch style dataset from dataframes.

        Args:
            df: The dataframe which has inputs, and the labels/targets.
            feature_cols: The name of columns which contain inputs.
                feature_cols can be a string if single column or can be a list of string if multiple columns.
            label_cols: The name of columns which contain the labels.
                label_cols can be a string or can be a list of string if multiple columns are used.

        Returns:
            np.array of inputs , labels if label_cols is not None else return np.array of inputs.
        """
        features = df.loc[:, feature_cols].values
        labels = df.loc[:, label_cols].values if label_cols is not None else None

        return cls(inputs=features, labels=labels)

    @classmethod
    def from_csv(
        cls,
        csv_path,
        feature_cols: Union[str, List[str]],
        label_cols: Union[str, List[str]] = None,
    ) -> TabularDataset:
        """Classmethod to create pytorch style dataset from csv file.

        Args:
            csv_path: The full path to csv.
            feature_cols: The name of columns which contain inputs.
                feature_cols can be a string if single column or can be a list of string if multiple columns.
            label_cols: The name of columns which contain the labels.
                label_cols can be a string or can be a list of string if multiple columns are used.

        Returns:
            np.array of inputs , labels if label_cols is not None else return np.array of inputs.
        """
        return cls.from_df(df=pd.read_csv(csv_path), feature_cols=feature_cols, label_cols=label_cols)

    def __len__(self):
        """__len__ method.

        Returns:
            The length of dataloader.
        """
        return self.inputs.shape[0]

    def __getitem__(self, item):
        """__getitem__ method.

        Args:
            item: idx

        Returns:
            Tensors of inputs , labels if labels is not None else returns Tensors of inputs.
        """
        feature = torch.tensor(self.inputs[item], dtype=torch.long)
        if self.labels is not None:
            labels = torch.tensor(self.labels[item], dtype=torch.long)
            return feature, labels

        return feature
