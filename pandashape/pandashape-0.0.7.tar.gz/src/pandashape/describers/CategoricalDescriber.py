from .Describer import Describer
import pandas as pd


class CategoricalDescriber(Describer):
    def get_section_header(self):
        return "Categorical data"

    def describe(self, df: pd.DataFrame):
        df_strings_or_objects = df.select_dtypes(object)

        if len(df_strings_or_objects.columns) == 0:
            return []

        messages = [
            "Some of your columns seem to represent categorical data as strings. Consider label-encoding these using the CategoricalEncoder:"]
        for column in df_strings_or_objects.columns:
            messages.append(f"- {column}: {df_strings_or_objects[column].nunique()} values")

        return messages
