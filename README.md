# pandas-save

Write Pandas and GeoPandas outputs to a local temporary directory, then copy the completed file to a network drive. This avoids the slow performance often caused by writing directly to network storage.

Supported outputs include CSV, Parquet, Pickle, Excel and GeoPandas files such as GeoPackage.

## Installation

Clone the repository and install it in editable mode:

```cmd
git clone https://github.com/hulsiejames/pandas-save.git
cd pandas-save
python -m pip install -e .
```

To include the development and test dependencies:

```cmd
python -m pip install pytest pyarrow openpyxl
```

## Example

```python
from pandas_save.api import to_csv, to_file

# Pandas
to_csv(df, r"P:\outputs\results.csv")

# GeoPandas
to_file(
    gdf,
    r"P:\outputs\results.gpkg",
    layer="results",
    driver="GPKG",
)
```

Temporary local files are removed automatically after the network copy completes.

## Tests

```cmd
python -m pytest
```
