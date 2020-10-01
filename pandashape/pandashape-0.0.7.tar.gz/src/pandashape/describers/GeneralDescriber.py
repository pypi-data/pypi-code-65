from .Describer import Describer


class GeneralDescriber(Describer):
    TEMP_SKEW_THRESHOLD = 0.4

    def get_section_header(self):
        return "General frame info"

    def describe(self, df):
        messages = [f"Shape: {df.shape}"]

        # NULLS
        columns_with_nulls = df.columns[df.isna().any()].array.to_numpy()
        if len(columns_with_nulls) > 0:
            messages.append(
                f"Columns with one or more null values: {columns_with_nulls}"
            )

        return messages
