import pytest
import pandas as pd
import numpy as np
from src.eurogreen_python_utils.dataframe_validations import (
    validate_df
)

@pytest.fixture
def wiod_industries_example():
    return ["A01", "A02", "A03", "B", "C10-C12", "C13-C15", "C16", "C17", "Q", "R_S", "T"]

@pytest.fixture
def wiod_multi_index_example(wiod_industries_example):
    return pd.MultiIndex.from_product(
        [["FI"], wiod_industries_example],
        names=["country_code3", "wiod_nace_r2"],
    )

@pytest.fixture
def wiod_df(wiod_multi_index_example):
    return pd.DataFrame(
        data=np.random.rand(11, 11),
        columns=wiod_multi_index_example,
        index=wiod_multi_index_example,
    )


def test_passes_as_expected(wiod_df, wiod_multi_index_example):

    assert validate_df(
        df_to_validate=wiod_df,
        expected_shape=(11,11),
        allow_missing=False,
        expected_index=wiod_multi_index_example,
        expected_column_index=wiod_multi_index_example,
        max_value=2.0,
    ) == 0


def test_type_validation(wiod_df):

    with pytest.raises(AssertionError):
        validate_df(
            df_to_validate=pd.Series([1,2,3]),
            expected_shape=(3,3),
            allow_missing=True,
        )


def test_shape_validation(wiod_df):

    with pytest.raises(AssertionError):
        validate_df(df_to_validate=wiod_df, expected_shape=(10,11), allow_missing=True)


def test_missing_validation():

    with pytest.raises(AssertionError):
        validate_df(
            df_to_validate=pd.DataFrame.from_dict({"v1": [np.nan], "v2": [1]}),
            expected_shape=(1,2),
            allow_missing=False,
        )


def test_index_validation():

    with pytest.raises(AssertionError):
        validate_df(
            df_to_validate=wiod_df,
            expected_shape=(11,11),
            allow_missing=False,
            expected_index=pd.Index(range(11)),
        )



def test_column_validation():

    with pytest.raises(AssertionError):
        validate_df(
            df_to_validate=wiod_df,
            expected_shape=(11,11),
            allow_missing=False,
            expected_column_index=pd.Index(range(11)),
        )

def test_max_value_validation():

    assert validate_df(
            df_to_validate=pd.DataFrame.from_dict({"v1": [2], "v2": [np.float64(100.0)]}),
            expected_shape=(1,2),
            allow_missing=False,
            max_value=100.00000000001
        ) == 0
    
    with pytest.raises(AssertionError):
        validate_df(
            df_to_validate=pd.DataFrame.from_dict({"v1": [2], "v2": [np.float64(100.0)]}),
            expected_shape=(1,2),
            allow_missing=False,
            max_value=99.0
        )
