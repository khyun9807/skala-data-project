import pytest
import pandas as pd
from src.clean import clean_nulls


@pytest.fixture
def sample_df():
    return pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", None]})


def test_clean_removes_nulls(sample_df):
    result = clean_nulls(sample_df, cols=["a"])
    assert result["a"].isna().sum() == 0


def test_shape_preserved(sample_df):
    result = clean_nulls(sample_df)
    assert result.shape[0] == 3
