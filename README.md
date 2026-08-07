# eurogreen-python-utils
Python utils related to data processing for the Eurogreen model family.

This package contains general utils not specific to a certain model or piece of data infrastructure. The main use so far is transforming data from one industry and product classification to another, with the module `categorization_transformations`. The `dataframe_validations` module is for simple data validation. For a more complete and sophisticated validation solution, check out [engarde](https://engarde.readthedocs.io/en/latest/).

## Usage

### Installation
```python
# Either using uv (uv is awesome, and you should probably be using it):
uv add "eurogreen_python_utils @ git+https://github.com/sisu-fingreen/eurogreen_python_utils"
# Or if using pip:
pip install eurogreen_python_utils@git+https://github.com/sisu-fingreen/eurogreen_python_utils

```

### Usage example
```python
import pandas as pd
import numpy as np
from eurogreen_python_utils import categorization_transformations as egput
from importlib.resources import files

# A few of the mapping files are included in the package, use one of them for reference
# Note that D industry is not disaggregated here
wiod_to_fingreen_industry_map_path = (
    files("eurogreen_python_utils.mappings")
    .joinpath("wiod-industry-to-fingreen-industry-map.ods")
)
wiod_to_fingreen_industry_map = pd.read_excel(
    io=wiod_to_fingreen_industry_map_path,
    sheet_name="wiod",
    index_col="wiod_nace_r2",
    engine="odf"
)

# Some example data
wiod_industries_example = ["A01", "A02", "A03", "B", "C10-C12", "C13-C15", "C16", "C17", "Q", "R_S", "T"]
wiod_multi_index_example = pd.MultiIndex.from_product(
    [["FI"], wiod_industries_example],
    names=["country_code3", "wiod_nace_r2"],
)
wiod_df = pd.DataFrame(
    data=np.random.rand(11, 11),
    columns=wiod_multi_index_example,
    index=wiod_multi_index_example,
)

# Transform rows
fingreen_rows = egput.transform_categorization_rows(
    df_to_transform=wiod_df,
    new_mapping=wiod_to_fingreen_industry_map,
    # These have to hold for the data and for the mapping table
    original_mapping_name="wiod_nace_r2",
    new_mapping_name="fingreen_industry_code"
)

# Transform columns
fingreen_columns = egput.transform_categorization_cols(
    df_to_transform=wiod_df,
    new_mapping=wiod_to_fingreen_industry_map,
    # These have to hold for the data and for the mapping table
    original_mapping_name="wiod_nace_r2",
    new_mapping_name="fingreen_industry_code"
)

# There is a convenience function to transform both rows and columns (aimed at io data)
fingreen_df = egput.transform_categorization_io(
    df_to_transform=wiod_df,
    new_mapping=wiod_to_fingreen_industry_map,
    # These have to hold for the data and for the mapping table
    original_mapping_name="wiod_nace_r2",
    new_mapping_name="fingreen_industry_code"
)

# Check out all the available functions
dir(egput)

# What about the dataframe validations?
from eurogreen_python_utils import dataframe_validations as egpuv

wiod_df_validations = egpuv.validate_df(
    df_to_validate=wiod_df,
    expected_shape=(11,11),
    allow_missing=False,
    # Optional
    expected_index=wiod_multi_index_example,
    expected_column_index=wiod_multi_index_example,
    max_value=3,
    df_name="wiod_df"
)

```
