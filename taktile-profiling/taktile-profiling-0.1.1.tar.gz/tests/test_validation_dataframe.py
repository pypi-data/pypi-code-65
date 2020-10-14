from datetime import date, datetime

import pandas as pd
import pytest
from profiling.utils import df_to_dict, to_pydantic
from pandas.testing import assert_frame_equal
from pydantic import ValidationError

dict_simple = {"Integer": [0], "Float": [0.0], "String": ["a"]}
df_simple = pd.DataFrame.from_dict(dict_simple)

dict_complex = {
    "Integer": [1, 2, 3],
    "Float": [None, 2.0, 3.0],
    "String": [None, "", "c"],
    "Categorical": ["a", "b", "c"],
    "Date Variable": [date(2020, 1, 1), date(2020, 1, 1), date(1, 1, 1)],
    "Datetime Variable": [
        datetime(2020, 1, 1),
        datetime(2020, 1, 1),
        datetime(1, 1, 1),
    ],
}

df_complex = pd.DataFrame.from_dict(dict_complex)
df_complex["Categorical"] = df_complex["Categorical"].astype("category")


@pytest.mark.parametrize(
    "input_df,expected_output", [(df_simple, dict_simple), (df_complex, dict_complex)]
)
def test_dict_conversion(input_df, expected_output):
    output = df_to_dict(input_df)
    assert output == expected_output


@pytest.mark.parametrize("input_df", [df_simple, df_complex])
def test_validation(input_df):
    DfPydantic = to_pydantic(input_df)
    input_dict = df_to_dict(input_df)
    assert DfPydantic.validate(input_dict)
    with pytest.raises(ValidationError):
        input_dict["Float"] = ["a"] * len(input_dict["Float"])
        DfPydantic.validate(input_dict)


@pytest.mark.parametrize("input_df", [df_simple, df_complex])
def test_nullable(input_df):
    DfPydantic = to_pydantic(input_df, nullable=False)
    with pytest.raises(ValidationError):
        input_df = input_df.copy()
        input_df.iloc[0, 0] = None
        input_dict = df_to_dict(input_df)
        DfPydantic.validate(input_dict)


@pytest.mark.parametrize("input_df", [df_simple, df_complex])
def test_roundtrip(input_df):
    input_dict = df_to_dict(input_df)
    DfPydantic = to_pydantic(input_df)
    validated_df = DfPydantic(**input_dict).to_df()
    assert_frame_equal(input_df, validated_df)
