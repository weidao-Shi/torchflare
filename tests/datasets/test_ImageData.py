# flake8: noqa
import collections

import albumentations as A
import pandas as pd
import torch
import torchvision

from torchflare.datasets.classification import ImageDataset

inputs = collections.namedtuple("inputs", ["path", "extension", "label_cols", "df", "image_col"])
df = pd.read_csv("tests/datasets/data/image_classification/csv_data/train.csv")
constants_df = inputs(
    path="tests/datasets/data/image_classification/csv_data/images",
    df=df,
    extension=".jpg",
    label_cols=["healthy", "multiple_diseases", "rust", "scab"],
    image_col="image_id",
)

folder_inputs = collections.namedtuple("folder_inputs", ["train_path", "test_path"])
folder_inputs = folder_inputs(
    train_path="tests/datasets/data/image_classification/folder_data/train_data",
    test_path="tests/datasets/data/image_classification/folder_data/test_data",
)


def test_data_from_df():
    def test_with_albumentations():
        augmentations = A.Compose([A.Resize(256, 256)])

        ds = ImageDataset.from_df(
            path=constants_df.path,
            df=constants_df.df,
            augmentations=augmentations,
            image_col=constants_df.image_col,
            label_cols=constants_df.label_cols,
            extension=constants_df.extension,
            convert_mode="RGB",
        )
        x, y = ds[0]

        assert torch.is_tensor(x) == True
        assert torch.is_tensor(y) == True
        assert x.shape == (3, 256, 256)
        assert y.shape[0] == 4
        # print(type(df.loc[: , 'image_id'].values[0]))

    # print(constants_df.df.head(cle))

    def test_with_torchvision():
        augmentations = torchvision.transforms.Compose(
            [torchvision.transforms.Resize((256, 256)), torchvision.transforms.ToTensor(),]
        )

        ds = ImageDataset.from_df(
            path=constants_df.path,
            df=constants_df.df,
            augmentations=augmentations,
            image_col=constants_df.image_col,
            label_cols=constants_df.label_cols,
            extension=constants_df.extension,
            convert_mode="RGB",
        )
        x, y = ds[0]

        assert torch.is_tensor(x) == True
        assert torch.is_tensor(y) == True
        # print(x.shape)
        assert x.shape == (3, 256, 256)
        assert y.shape[0] == 4

    def test_with_torchvision_no_tensor():
        augmentations = torchvision.transforms.Compose([torchvision.transforms.Resize((256, 256))])

        ds = ImageDataset.from_df(
            path=constants_df.path,
            df=constants_df.df,
            augmentations=augmentations,
            image_col=constants_df.image_col,
            label_cols=constants_df.label_cols,
            extension=constants_df.extension,
            convert_mode="RGB",
        )
        x, y = ds[0]

        assert torch.is_tensor(x) == True
        assert torch.is_tensor(y) == True
        assert x.shape == (3, 256, 256)
        assert y.shape[0] == 4

    def test_for_inference():

        ds = ImageDataset.from_df(
            path=constants_df.path,
            df=constants_df.df,
            augmentations=None,
            image_col=constants_df.image_col,
            label_cols=None,
            extension=constants_df.extension,
            convert_mode="RGB",
        )
        x = ds[0]

        assert torch.is_tensor(x) == True
        # assert torch.is_tensor(y) == True
        # assert x.shape == (3, 256, 256)
        # assert y.shape[0] == 4
        # print(y)

    test_with_albumentations()
    test_with_torchvision()
    test_with_torchvision_no_tensor()
    test_for_inference()


def test_from_folders():
    def test_training():
        augmentations = A.Compose([A.Resize(256, 256)])

        ds = ImageDataset.from_folders(path=folder_inputs.train_path, augmentations=augmentations, convert_mode="RGB",)

        x, y = ds[0]
        assert torch.is_tensor(x) == True
        assert torch.is_tensor(y) == True
        assert x.shape == (3, 256, 256)
        assert torch.is_tensor(y) == True

    def test_inference():
        ds = ImageDataset.from_folders(path=folder_inputs.test_path, augmentations=None, convert_mode="RGB")
        x = ds[0]

        assert torch.is_tensor(x) == True
        assert len(x.shape) == 3

    test_inference()
    test_training()
