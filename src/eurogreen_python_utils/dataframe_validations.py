import pandas as pd
from math import isclose

def validate_df(
    df_to_validate: pd.DataFrame,
    expected_shape: tuple,
    allow_missing: bool,
    expected_index: pd.Index = None,
    expected_column_index: pd.Index = None,
    max_value: float = None,
    df_name: str = "",
) -> int:

    assert isinstance(df_to_validate, pd.DataFrame), "Not a DataFrame!"

    assert (df_to_validate.shape == expected_shape), "Wrong shape!"
    
    if not allow_missing:
        assert not df_to_validate.isna().any().any(), "Missing values!"
    
    if not expected_index is None:
        pd.testing.assert_index_equal(df_to_validate.index, expected_index)

    if not expected_column_index is None:
        pd.testing.assert_index_equal(df_to_validate.columns, expected_column_index)
        
    if not max_value is None:
        df_max = df_to_validate.max(axis=None)
        assert df_max <= max_value or isclose(df_max, max_value), "Too big values!"
    
    print("Validations for", df_name, "passed.")

    return 0
