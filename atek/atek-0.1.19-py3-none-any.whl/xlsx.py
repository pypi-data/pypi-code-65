# %% imports
import pandas as pd
import toolz.curried as tz
from pathlib import Path
from atek import valid_path
from typing import Union, Dict
from dataclasses import dataclass
from fnmatch import fnmatch

__all__ = ["fcode", "to_xlsx"]

# %% writer
def writer(path: Union[str, Path, pd.ExcelWriter]) -> pd.ExcelWriter:
    if isinstance(path, pd.ExcelWriter) and path.engine == "xlsxwriter":
        return path

    if isinstance(path, pd.ExcelWriter) and path.engine != "xlsxwriter":
        path = path.path

    return pd.ExcelWriter(valid_path(path), engine="xlsxwriter")


# %% calc_column_width
def calc_column_width(data: pd.DataFrame, min_width: int=10, max_width: int=50
    ) -> Dict[str,int]:

    value_width = {
        col: data[col]
            .apply(lambda x: len(str(x)))
            .max()
        for col in data.columns
    }
    header_width = {col: len(col) for col in data.columns}
    min_width = {col: min_width for col in data.columns}
    max_width = {col: max_width for col in data.columns}
    width = tz.pipe(
        tz.merge_with(
            max
            ,value_width
            ,header_width
            ,min_width
        )
        ,lambda d: tz.merge_with(min, d, max_width)
    )
    return width

# calc_column_width(data, 4, 20)


# %% Format
@dataclass(frozen=True)
class Format:
    pattern: str
    codes: Dict[str,Union[str,int]]


# %% fcode
def fcode(pattern: str, **kwargs) -> Format:
    return Format(pattern, kwargs)


# %% match_formats
def match_formats(data: pd.DataFrame, *formats: Format) -> Dict[str,Format]:
    matches = {}
    for col in data.columns:
        for fmt in formats:
            if col not in matches:
                pass
            if fnmatch(col, fmt.pattern):
                matches[col] = fmt
    return matches

# match_formats(
#     data,
#     F.from_vargs("*Amount", num_format="#,##0.00"),
#     F.from_vargs("*Amount/Order", num_format="#,##0"),
# )


# %% to_xlsx
def to_xlsx(data: pd.DataFrame, path: Union[str, Path, pd.ExcelWriter],
    sheet_name: str, *formats: Format,
    index: bool=False, start_row: int=0, start_column: int=0,
    min_col_width: int=10, max_col_width: int=50,
    freeze_column: int=0) -> Path:

    with writer(path) as file:

        # Write data
        data.to_excel(
            file,
            sheet_name=sheet_name,
            index=index,
            startrow=start_row,
            startcol=start_column,
        )

        # Get reference to sheet
        ws = file.sheets[sheet_name]
        widths = calc_column_width(data, min_col_width, max_col_width)
        matched_formats = match_formats(data, *formats)

        for idx, col in enumerate(data.columns, start=start_column):
            # Get data type and set default format
            dtype = data[col].dtype.name.lower()
            num_format = (
                "" if dtype == "object" else
                "#,##0" if "int" in dtype else
                "#,##0.00" if "float" in dtype else
                "yyyy-mm-dd" if "date" in dtype else
                ""
            )
            align = (
                "left" if dtype == "object" else
                "left" if "date" in dtype else
                "right"
            )
            default = {
                "text_wrap": True,
                "num_format": num_format,
                "align": align,
                "valign": "top",
            }

            # set column format
            if col in matched_formats:
                codes = {
                    **default,
                    **matched_formats[col].codes
                }
                if col == "Month": print(codes)
                fmt = file.book.add_format(codes)
            else:
                fmt = file.book.add_format(default)

            ws.set_column(
                first_col=idx,
                last_col=idx,
                width=widths[col],
                cell_format=fmt
            )

        # add worksheet table
        ws.add_table(
            start_row,
            start_column,
            len(data) + start_row,
            len(data.columns)-1 + start_column,
            {
                "name": sheet_name.replace(" ", "_"),
                "header_row": True,
                "autofilter": False,
                "banded_rows": True,
                "style": "Table Style Light 1",
                "columns": [{"header": col} for col in data.columns],
            },
        )

        # format header row
        for idx, col in enumerate(data.columns, start=start_column):
            fmt = file.book.add_format()
            align = (
                "left" if dtype == "object" else
                "left" if "date" in dtype else
                "right"
            )
            fmt.set_align(align)
            fmt.set_align("bottom")
            ws.write(start_row, idx, col, fmt)

        # freeze panes
        ws.freeze_panes(start_row + 1, start_column + freeze_column)

    return valid_path(file.path)
