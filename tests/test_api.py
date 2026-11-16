"""Tests for the public functions in pandas_save.api."""

# # # # IMPORTS # # # #
# Built-Ins
from pathlib import Path

# 3rd Party
import geopandas as gpd
import pandas as pd
from pandas.testing import assert_frame_equal
from shapely.geometry import Point

# Local
from pandas_save.api import (
    to_csv,
    to_excel_staged,
    to_file,
    to_parquet,
    to_pickle,
)

# # # # FUNCTIONS # # # #


def create_test_dataframe():
    """Create a small DataFrame for testing."""
    return pd.DataFrame(
        {
            "zone_id": ["E001", "E002", "E003"],
            "jobs": [1250, 980, 1430],
            "change": [0.15, -0.08, 0.22],
        }
    )


def create_test_geodataframe():
    """Create a small GeoDataFrame for testing."""
    return gpd.GeoDataFrame(
        {
            "zone_id": ["E001", "E002", "E003"],
            "jobs": [1250, 980, 1430],
        },
        geometry=[
            Point(-2.2426, 53.4808),
            Point(-1.6178, 54.9783),
            Point(-1.5491, 53.8008),
        ],
        crs="EPSG:4326",
    )


def assert_no_partial_files(directory):
    """Check that no unfinished partial files remain."""
    partial_files = list(Path(directory).rglob("*.partial"))

    assert not partial_files, f"Partial files were not cleaned up: {partial_files}"


def test_to_csv(tmp_path):
    """Test writing and reading a staged CSV file."""
    dataframe = create_test_dataframe()

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.csv"

    result = to_csv(
        dataframe,
        destination,
        network_roots=(network_directory,),
    )

    assert result == destination
    assert destination.exists()
    assert destination.is_file()

    saved_dataframe = pd.read_csv(destination)

    assert_frame_equal(saved_dataframe, dataframe)
    assert_no_partial_files(network_directory)


def test_to_parquet(tmp_path):
    """Test writing and reading a staged Parquet file."""
    dataframe = create_test_dataframe()

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.parquet"

    result = to_parquet(
        dataframe,
        destination,
        network_roots=(network_directory,),
    )

    assert result == destination
    assert destination.exists()
    assert destination.is_file()

    saved_dataframe = pd.read_parquet(destination)

    assert_frame_equal(saved_dataframe, dataframe)
    assert_no_partial_files(network_directory)


def test_to_pickle(tmp_path):
    """Test writing and reading a staged Pickle file."""
    dataframe = create_test_dataframe()

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.pkl"

    result = to_pickle(
        dataframe,
        destination,
        network_roots=(network_directory,),
    )

    assert result == destination
    assert destination.exists()
    assert destination.is_file()

    saved_dataframe = pd.read_pickle(destination)

    assert_frame_equal(saved_dataframe, dataframe)
    assert_no_partial_files(network_directory)


def test_to_excel_staged(tmp_path):
    """Test writing and reading a staged Excel file."""
    dataframe = create_test_dataframe()

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.xlsx"

    result = to_excel_staged(
        dataframe,
        destination,
        network_roots=(network_directory,),
        sheet_name="Results",
    )

    assert result == destination
    assert destination.exists()
    assert destination.is_file()

    saved_dataframe = pd.read_excel(
        destination,
        sheet_name="Results",
    )

    assert_frame_equal(saved_dataframe, dataframe)
    assert_no_partial_files(network_directory)


def test_to_file_geopackage(tmp_path):
    """Test writing and reading a staged GeoPackage."""
    geodataframe = create_test_geodataframe()

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.gpkg"

    result = to_file(
        geodataframe,
        destination,
        network_roots=(network_directory,),
        layer="results",
        driver="GPKG",
    )

    assert result == destination
    assert destination.exists()
    assert destination.is_file()

    saved_geodataframe = gpd.read_file(
        destination,
        layer="results",
    )

    expected = geodataframe.reset_index(drop=True)
    actual = saved_geodataframe.reset_index(drop=True)

    assert actual.crs == expected.crs
    assert actual["zone_id"].tolist() == expected["zone_id"].tolist()
    assert actual["jobs"].tolist() == expected["jobs"].tolist()
    assert actual.geometry.equals(expected.geometry)

    assert_no_partial_files(network_directory)


def test_to_csv_overwrite_true(tmp_path):
    """Test that overwrite=True replaces an existing output."""
    original_dataframe = create_test_dataframe()

    replacement_dataframe = pd.DataFrame(
        {
            "zone_id": ["NEW001", "NEW002"],
            "jobs": [5000, 6000],
            "change": [1.5, 2.5],
        }
    )

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.csv"

    to_csv(
        original_dataframe,
        destination,
        network_roots=(network_directory,),
    )

    to_csv(
        replacement_dataframe,
        destination,
        network_roots=(network_directory,),
        overwrite=True,
    )

    saved_dataframe = pd.read_csv(destination)

    assert_frame_equal(saved_dataframe, replacement_dataframe)
    assert_no_partial_files(network_directory)


def test_to_csv_overwrite_false(tmp_path):
    """Test that overwrite=False protects an existing output."""
    dataframe = create_test_dataframe()

    network_directory = tmp_path / "network"
    network_directory.mkdir()

    destination = network_directory / "results.csv"

    to_csv(
        dataframe,
        destination,
        network_roots=(network_directory,),
    )

    try:
        to_csv(
            dataframe,
            destination,
            network_roots=(network_directory,),
            overwrite=False,
        )

    except FileExistsError:
        pass

    else:
        raise AssertionError("Expected FileExistsError when overwrite=False.")

    assert_no_partial_files(network_directory)
