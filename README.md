# eurogreen-python-utils
Python utils related to data processing for the Eurogreen model family

This package contains general utils not specific to a certain model or piece of data infrastructure. The main use so far is transforming data from one industry and product classification to another, with the module `categorization_transformations`. The `dataframe_validations` module is for simple data validation. For a more complete and sophisticated validation solution, check out [engarde](https://engarde.readthedocs.io/en/latest/).

## Usage

### Installation
```
# Either using eg. uv:
uv add "eurogreen_python_utils @ git+https://github.com/sisu-fingreen/eurogreen_python_utils"
# Or if using pip:
pip install eurogreen_python_utils@git+https://github.com/sisu-fingreen/eurogreen_python_utils

```


### Categorization transformations
```
from eurogreen_python_utils import categorization_transformations as eguct


```