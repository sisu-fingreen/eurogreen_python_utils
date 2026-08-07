import pytest
import pandas as pd
import numpy as np
from src.eurogreen_python_utils.categorization_transformations import (
    transform_categorization_rows,
    transform_categorization_cols,
    io_from_wiod_industry_to_fingreen_industry,
    series_from_wiod_industry_to_fingreen_industry,
    io_from_william_industry_to_fingreen_industry,
)

# WIOD fixtures

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

@pytest.fixture
def wiod_series(wiod_multi_index_example):
    return pd.Series(
        data=np.random.rand(11,1).flatten(),
        index=wiod_multi_index_example,
    )

@pytest.fixture
def wiod_fingreen_industry_map():
    res = (
        pd.read_excel(
            "src/mappings/wiod-industry-to-fingreen-industry-map.ods",
            sheet_name="wiod",
            engine="odf",
            index_col="wiod_nace_r2",
        )
    )
    return res

# William fixtures

@pytest.fixture
def william_industries_example():
    return ["CROPS", "ANIMALS", "FORESTRY", "OTHER_SERVICES", "HEALTH", "ENTERTAIMENT", "PRIVATE_HOUSEHOLDS"] # ENTERTAIMENT (sic)

@pytest.fixture
def william_multi_index_example(william_industries_example):
    return pd.MultiIndex.from_product(
        [["FIN"], william_industries_example],
        names=["country_code3", "william_industry_name"],
    )

@pytest.fixture
def william_df(william_multi_index_example):
    return pd.DataFrame(
        data=np.random.rand(7, 7),
        columns=william_multi_index_example,
        index=william_multi_index_example,
    )

@pytest.fixture
def william_series(william_multi_index_example):
    return pd.Series(
        data=np.random.rand(7,1).flatten(),
        index=william_multi_index_example,
    )

@pytest.fixture
def william_fingreen_industry_map():
    res = (
        pd.read_excel(
            "src/mappings/william-industry-to-fingreen-industry-map.ods",
            sheet_name="william",
            engine="odf",
            index_col="william_industry_name",
        )
    )
    return res

# pefa fixtures
@pytest.fixture
def eurostat_pefa_fingreen_industry_map():
    return pd.read_excel(
        "src/mappings/eurostat-pefa-to-fingreen-industry-map-d-agg.ods",
        sheet_name="pefa",
        engine="odf",
        index_col="nace_r2",
    )

@pytest.fixture
def pefa_df():
    return pd.DataFrame.from_dict(
        data={
            "index": [
                'Brown coal and peat',
                'Energy losses all kinds of (during extraction, distribution, storage and transformation, and dissipative heat from end use)',
                'Fossil non-renewable natural energy inputs',
                'Liquid biofuels',
                'Natural energy inputs, energy products and energy residuals',
                'Nuclear fuel',
                'Wind based renewable natural energy inputs',
                'Wood, wood waste and other solid biomass, charcoal'
            ],
            "columns": ["A01", "A02", "A03", "K64", "K65", "K66"],
            "data": np.random.rand(8,6),
            "index_names": ["prod_nrg_description"],
            "column_names": ["nace_r2"]
        },
        orient="tight",
    )

def test_column_sums(wiod_df, wiod_fingreen_industry_map):
    fingreen_df = transform_categorization_rows(
        wiod_df,
        wiod_fingreen_industry_map,
        original_mapping_name="wiod_nace_r2",
        new_mapping_name="fingreen_industry_code",
    )
    original_colsums = wiod_df.sum()
    new_colsums = fingreen_df.sum()
    print("orig:", original_colsums, "new:", new_colsums)
    pd.testing.assert_series_equal(original_colsums, new_colsums)

def test_row_sums(wiod_df, wiod_fingreen_industry_map):
    fingreen_df = transform_categorization_cols(
        wiod_df,
        wiod_fingreen_industry_map,
        original_mapping_name="wiod_nace_r2",
        new_mapping_name="fingreen_industry_code",
    )
    original_rowsums = wiod_df.sum(axis=1)
    new_rowsums = fingreen_df.sum(axis=1)
    print("orig:", original_rowsums, "new:", new_rowsums)
    pd.testing.assert_series_equal(original_rowsums, new_rowsums)

def test_total_sum_wiod(wiod_df, wiod_fingreen_industry_map):
    fingreen_df = io_from_wiod_industry_to_fingreen_industry(wiod_df, wiod_fingreen_industry_map)
    original_sum = wiod_df.sum().sum()
    new_sum = fingreen_df.sum().sum()
    assert new_sum == pytest.approx(original_sum), "Total sum of values has changed, it should not!"

def test_series_transformation(wiod_series, wiod_fingreen_industry_map):
    fingreen_series = series_from_wiod_industry_to_fingreen_industry(wiod_series, wiod_fingreen_industry_map)
    original_sum = wiod_series.sum()
    new_sum = fingreen_series.sum()
    print(wiod_series)
    print(fingreen_series)
    assert new_sum == pytest.approx(original_sum), "Total sum of values has changed, it should not!"

def test_total_sum_william(william_df, william_fingreen_industry_map):
    fingreen_df = io_from_william_industry_to_fingreen_industry(william_df, william_fingreen_industry_map)
    original_sum = william_df.sum().sum()
    new_sum = fingreen_df.sum().sum()
    assert new_sum == pytest.approx(original_sum), "Total sum of values has changed, it should not!"

def test_output_index_wiod(wiod_df, wiod_fingreen_industry_map):
    fingreen_df = io_from_wiod_industry_to_fingreen_industry(wiod_df, wiod_fingreen_industry_map)
    assert fingreen_df.index.names == ['country_code3', 'fingreen_industry_code']
    assert fingreen_df.columns.names == ['country_code3', 'fingreen_industry_code']

def test_output_index_william(william_df, william_fingreen_industry_map):
    fingreen_df = io_from_william_industry_to_fingreen_industry(william_df, william_fingreen_industry_map)
    assert fingreen_df.index.names == ['country_code3', 'fingreen_industry_code']
    assert fingreen_df.columns.names == ['country_code3', 'fingreen_industry_code']

def test_index_matching_assertion(wiod_df, wiod_fingreen_industry_map):
    wiod_fingreen_industry_map.reset_index(inplace=True)
    with pytest.raises(AssertionError) as excinfo:
        io_from_wiod_industry_to_fingreen_industry(wiod_df, wiod_fingreen_industry_map)
    assert "Original mapping variable should be in the index in both or neither of the dataframes." in str(excinfo.value)

def test_transform_with_no_disaggregation(pefa_df, eurostat_pefa_fingreen_industry_map):
    fingreen_df = transform_categorization_cols(
        pefa_df,
        eurostat_pefa_fingreen_industry_map,
        original_mapping_name="nace_r2",
        new_mapping_name="fingreen_industry_code",
    )
    original_rowsums = pefa_df.sum(axis=1)
    new_rowsums = fingreen_df.sum(axis=1)
    print("orig:", original_rowsums, "new:", new_rowsums)
    pd.testing.assert_series_equal(original_rowsums, new_rowsums)

def test_index_order_agnosticity(wiod_df, wiod_fingreen_industry_map):
    fingreen_df = io_from_wiod_industry_to_fingreen_industry(
        wiod_df=wiod_df.reorder_levels([1,0]),
        wiod_fingreen_industry_map=wiod_fingreen_industry_map,
    )
    original_sum = wiod_df.sum().sum()
    new_sum = fingreen_df.sum().sum()
    assert new_sum == pytest.approx(original_sum), "Total sum of values has changed, it should not!"
