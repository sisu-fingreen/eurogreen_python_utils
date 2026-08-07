import pandas as pd
# import numpy as np

# wiod_industries_example = ["A01", "A02", "A03", "B", "C10-C12", "C13-C15", "C16", "C17", "Q", "R_S", "T"]

# wiod_fingreen_industry_map = pd.read_excel(
#     "source-data/mappings/wiod-industry-to-fingreen-industry-map.ods",
#     sheet_name="wiod",
#     engine="odf",
#     index_col="wiod_nace_r2",
# )

# wiod_df = pd.DataFrame(
#     data=np.random.rand(11, 11),
#     columns=pd.MultiIndex.from_product(
#         [["FI"], wiod_industries_example],
#         names=["country_code3", "wiod_nace_r2"],
#     ),
#     index=pd.MultiIndex.from_product(
#         [["FI"], wiod_industries_example],
#         names=["country_code3", "wiod_nace_r2"],
#     ),
# )

def transform_categorization_rows(
    df_to_transform: pd.DataFrame,
    new_mapping: pd.DataFrame,
    original_mapping_name: str,
    new_mapping_name: str,
) -> pd.DataFrame:
    
    assert df_to_transform.columns.nlevels in [1,2], "Column index must have depth of 1 or 2"

    # Check that the mapping variable is in the index in both or neither dataframe otherwise fail
    mapping_is_in_index_in_df_to_transform = original_mapping_name in df_to_transform.index.names
    mapping_is_in_index_in_map = original_mapping_name in new_mapping.index.names
    assert not (mapping_is_in_index_in_df_to_transform ^ mapping_is_in_index_in_map), (
        "Original mapping variable should be in the index in both or neither of the dataframes."
    )

    index_vars_for_result = [
        new_mapping_name if x == original_mapping_name else x for x in df_to_transform.index.names
    ]

    df_to_transform_copy = df_to_transform.copy()

    # Everything is easier if we flatten the multi-level columns first
    df_to_transform_has_multi_index_columns = isinstance(df_to_transform.columns, pd.MultiIndex)
    if df_to_transform_has_multi_index_columns:
        df_to_transform_copy.columns = df_to_transform.columns.to_flat_index()

    mapped_df = df_to_transform_copy.join(new_mapping, how="left", on=original_mapping_name)
    
    assert mapped_df[new_mapping_name].notna().all(), "All categories were not mapped"
    
    # We don't really need a relationship column, which is in the mapping for human readability only
    if ("relationship" in mapped_df.columns):
        mapped_df.drop(columns=["relationship"], inplace=True)
    
    has_disaggregation_coefficient = "disaggregation_coefficient" in new_mapping.columns

    if has_disaggregation_coefficient:
        def summing_function(group: pd.DataFrame):
            # Sum the numeric columns multiplied by the disaggregation coefficient.
            # This function will be applied to groups by the new industry code.
            res = (
                group
                .select_dtypes(include="number")
                .multiply(
                    group["disaggregation_coefficient"].where(group["disaggregation_coefficient"].notna(), 1.0),
                    axis="index"
                )
                .drop("disaggregation_coefficient", axis="columns")
                .sum()
            )
            return res
    else:
        def summing_function(group: pd.DataFrame):
            res = group.select_dtypes(include="number").sum()
            return res

    res = (
        mapped_df
        # groupby sorts the group keys by default, so in the result we will get indexes that are sorted
        .groupby(index_vars_for_result)
        .apply(func=summing_function, include_groups=False)
    )
    # Back to multi-level columns
    if df_to_transform_has_multi_index_columns:
        res.columns = pd.MultiIndex.from_tuples(res.columns, names=df_to_transform.columns.names)
    else:
        res.columns.names = df_to_transform.columns.names
    
    return res

def transform_categorization_cols(
    df_to_transform: pd.DataFrame,
    new_mapping: pd.DataFrame,
    original_mapping_name: str,
    new_mapping_name: str,
) -> pd.DataFrame:

    # We just transpose forth and back to transfrom columns instead of rows
    
    df_to_transform_transposed = df_to_transform.T

    res_transposed = transform_categorization_rows(
        df_to_transform=df_to_transform_transposed,
        new_mapping=new_mapping,
        original_mapping_name=original_mapping_name,
        new_mapping_name=new_mapping_name,
    )
    res = res_transposed.T
    return res

def transform_categorization_io(
    df_to_transform: pd.DataFrame,
    new_mapping: pd.DataFrame,
    original_mapping_name: str,
    new_mapping_name: str,
) -> pd.DataFrame:
    
    df_to_transform_rows_transformed = transform_categorization_rows(
        df_to_transform=df_to_transform,
        new_mapping=new_mapping,
        original_mapping_name=original_mapping_name,
        new_mapping_name=new_mapping_name,
    )
    df_to_transform_rows_and_cols_transformed = transform_categorization_cols(
        df_to_transform=df_to_transform_rows_transformed,
        new_mapping=new_mapping,
        original_mapping_name=original_mapping_name,
        new_mapping_name=new_mapping_name,
    )
    return df_to_transform_rows_and_cols_transformed

def transform_categorization_series(
    series_to_transform: pd.Series,
    new_mapping: pd.DataFrame,
    original_mapping_name: str,
    new_mapping_name: str,
) -> pd.Series:

    df_to_transform = pd.DataFrame(series_to_transform)
    res = (
        transform_categorization_rows(
            df_to_transform,
            new_mapping,
            original_mapping_name=original_mapping_name,
            new_mapping_name=new_mapping_name
        )
        .squeeze()
    )
    return res

def io_from_wiod_industry_to_fingreen_industry(
    wiod_df: pd.DataFrame,
    wiod_fingreen_industry_map: pd.DataFrame,
) -> pd.DataFrame:
    
    res = transform_categorization_io(
        df_to_transform=wiod_df,
        new_mapping=wiod_fingreen_industry_map,
        original_mapping_name="wiod_nace_r2",
        new_mapping_name="fingreen_industry_code",
    )
    return res

def series_from_wiod_industry_to_fingreen_industry(
    wiod_series: pd.Series,
    wiod_fingreen_industry_map: pd.DataFrame,
) -> pd.Series:

    res = transform_categorization_series(
        series_to_transform=wiod_series,
        new_mapping=wiod_fingreen_industry_map,
        original_mapping_name="wiod_nace_r2",
        new_mapping_name="fingreen_industry_code",
    )
    return res

def io_from_william_industry_to_fingreen_industry(
    william_df: pd.DataFrame,
    william_fingreen_industry_map: pd.DataFrame,
) -> pd.DataFrame:
    
    res = transform_categorization_io(
        df_to_transform=william_df,
        new_mapping=william_fingreen_industry_map,
        original_mapping_name="william_industry_name",
        new_mapping_name="fingreen_industry_code",
    )
    return res

def transform_rows_from_prod_nrg_to_custom(
    df_to_transform: pd.DataFrame,
    prod_nrg_to_custom_map: pd.DataFrame,
) -> pd.DataFrame:

    res = transform_categorization_rows(
        df_to_transform=df_to_transform,
        new_mapping=prod_nrg_to_custom_map,
        original_mapping_name="prod_nrg",
        new_mapping_name="e_product_custom",
    )
    return res

def transform_cols_from_e_product_custom_to_eurogreen(
    df_to_transform: pd.DataFrame,
    e_product_custom_to_eurogreen_map: pd.DataFrame,
) -> pd.DataFrame:

    res = transform_categorization_cols(
        df_to_transform=df_to_transform,
        new_mapping=e_product_custom_to_eurogreen_map,
        original_mapping_name="e_product_custom",
        new_mapping_name="eurogreen_e_product"
    )
    return res
