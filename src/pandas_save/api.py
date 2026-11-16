"""API functionality using core module."""

# # # # IMPORTS # # # #
from __future__ import annotations

# Built-Ins
import os

import geopandas as gpd

# 3rd Party
import pandas as pd

# Local
from pandas_save.core import DEFAULT_NETWORK_ROOTS, staged_write

# # # # CONSTANTS # # # #


# # # # FUNCTIONS # # # #


def to_file(
    geo_dataframe: gpd.GeoDataFrame,
    destination: str | os.PathLike,
    *,
    network_roots=DEFAULT_NETWORK_ROOTS,
    overwrite=True,
    **kwargs,
) -> None:
    kwargs.setdefault("index", False)

    return staged_write(
        destination,
        geo_dataframe.to_file,
        writer_kwargs=kwargs,
        network_roots=network_roots,
        overwrite=overwrite,
    )


def to_csv(
    dataframe: pd.DataFrame,
    destination: str | os.PathLike,
    *,
    network_roots=DEFAULT_NETWORK_ROOTS,
    overwrite=True,
    **kwargs,
):
    kwargs.setdefault("index", False)

    return staged_write(
        destination,
        dataframe.to_csv,
        writer_kwargs=kwargs,
        network_roots=network_roots,
        overwrite=overwrite,
    )


def to_parquet(
    dataframe: pd.DataFrame,
    destination: str | os.PathLike,
    *,
    network_roots=DEFAULT_NETWORK_ROOTS,
    overwrite=True,
    **kwargs,
):
    kwargs.setdefault("index", False)

    return staged_write(
        destination,
        dataframe.to_parquet,
        writer_kwargs=kwargs,
        network_roots=network_roots,
        overwrite=overwrite,
    )


def to_pickle(
    dataframe: pd.DataFrame,
    destination: str | os.PathLike,
    *,
    network_roots=DEFAULT_NETWORK_ROOTS,
    overwrite=True,
    **kwargs,
):
    return staged_write(
        destination,
        dataframe.to_pickle,
        writer_kwargs=kwargs,
        network_roots=network_roots,
        overwrite=overwrite,
    )


def to_excel_staged(
    dataframe: pd.DataFrame,
    destination: str | os.PathLike,
    *,
    network_roots=DEFAULT_NETWORK_ROOTS,
    overwrite=True,
    **kwargs,
):
    kwargs.setdefault("index", False)

    return staged_write(
        destination,
        dataframe.to_excel,
        writer_kwargs=kwargs,
        network_roots=network_roots,
        overwrite=overwrite,
    )
