import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
import time
import requests

def list_is_numeric(x: list) -> bool:
    res = all(isinstance(val, (int, float)) for val in x)
    return res

def array_or_series_is_numeric(x: np.ndarray | pd.Series) -> bool:
    res = np.issubdtype(x.dtype, np.number)
    return res

def object_is_numeric(x):
    
    if isinstance(x, list):
        return list_is_numeric(x)
    elif isinstance(x, (pd.Series, np.ndarray)):
        return array_or_series_is_numeric(x)
    elif isinstance(x, (int, float)):
        return True
    elif isinstance(x, pd.DataFrame):
        return all(x.dtypes.map(is_numeric_dtype))

    return False

def object_is_integers(x):

    if isinstance(x, list):
        return all(isinstance(val, int) for val in x)
    elif isinstance(x, (pd.Series, np.ndarray)):
        return np.issubdtype(x.dtype, np.integer)
    elif isinstance(x, int):
        return True

    return False

def _get_conversion_factor(from_year: int, to_year: int) -> float:

    query = {
        'query': [{
            'code': 'timeperiod_y',
            'selection': {
                'filter': 'item',
                'values': [to_year, from_year]
                }
        }],
        'response': {'format': 'json-stat2'}
    }

    # Get data from API
    try:
        response = requests.post(
            url="https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/khi/11xy.px",
            json=query
        )
        
        response.raise_for_status()
        response_data = response.json()
        scores_series = pd.Series(
            data=response_data["value"],
            index=response_data["dimension"]["timeperiod_y"]["category"]["index"]
        )
        conversion_factor = scores_series.loc[str(to_year)] / scores_series.loc[str(from_year)]

    except Exception as e:
        raise RuntimeError(f"Failed to get conversion factor for years {from_year}-{to_year}: {str(e)}")
    
    return(conversion_factor)

def _apply_conversion_factors(x, from_years, to_years, conversion_factors: dict):

    result = []
    for val, f, t in zip(x, from_years, to_years):
        if f == t:
            result.append(val)
        else:
            result.append(val * conversion_factors[(f, t)])
    
    return result

def convert_eur_value_between_years(x, from_years, to_years):
    """
    Convert euro values between years adjusting for inflation using StatFin API.

    Parameters:
    x (int, float, list, pd.Series or np.ndarray): Values to convert
    from_years (int, list, pd.Series or np.ndarray): Starting year(s) for conversion
    to_years (int, list, pd.Series or np.ndarray): Target year(s) for conversion

    Returns:
    int, float, list, pd.Series or np.ndarray: Converted values, matching type of x when possible
    
    Note that dtype of x is not necessarily matched by the return value, and will most likely be np.float64
    """
    
    # Input validation

    assert object_is_numeric(x), "x must be numeric"
    assert object_is_integers(from_years), "from_years must be integer(s)"
    assert object_is_integers(to_years), "to_years must be integer(s)"

    x_orig_type = type(x)
    # Convert single values to lists for consistent processing
    if isinstance(x, (int, float)):
        x = [x]
    if isinstance(from_years, int):
        from_years = [from_years] * len(x)
    if isinstance(to_years, int):
        to_years = [to_years] * len(x)
    
    assert len(x) == len(from_years) == len(to_years), "Input lengths don't match"

    # If no conversion needed, return original values
    if all(f == t for f, t in zip(from_years, to_years)):
        return x.copy()

    # Create unique year pairs
    year_pairs = pd.DataFrame({'from': from_years, 'to': to_years})
    year_pairs = year_pairs.drop_duplicates()
    year_pairs = year_pairs[year_pairs['from'] != year_pairs['to']]

    # Get conversion factors for each unique year pair
    conversion_factors = {}
    
    # use rate limit only if we make multiple calls
    if year_pairs.shape[0] > 1:
        sleep_time =  3.1
    else:
        sleep_time = 0

    for i, row in year_pairs.iterrows():
        from_year = int(row['from'])
        to_year = int(row['to'])

        conversion_factors[(from_year, to_year)] = _get_conversion_factor(from_year, to_year)
        
        # Respect API rate limits
        time.sleep(sleep_time)

    # Apply conversion factors to input values

    if x_orig_type == pd.DataFrame:
        result = x.apply(
            lambda y: _apply_conversion_factors(y, from_years, to_years, conversion_factors)
        )
        return result

    result = _apply_conversion_factors(x, from_years, to_years, conversion_factors)
    if x_orig_type == float or x_orig_type == int:
        result = float(result[0])
    elif x_orig_type == np.ndarray:
        result = np.array(result)
    elif x_orig_type == pd.Series:
        result = pd.Series(result, index=x.index)

    return result
