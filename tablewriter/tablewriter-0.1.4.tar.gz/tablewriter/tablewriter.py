# -*- coding: utf-8 -*-
"""Created on some day of 2018 or 2019.

@author: cottephi@gmail.com
"""

import os
import time
import tempfile
from copy import deepcopy
from transparentpath import TransparentPath as Path
from typing import Any, Dict, TypeVar, Union

import pandas as pd

T = TypeVar("T")
DONE = "  ...done"
LATEX_TEXT_COLOR = r"\textcolor{"


class TableWriter(object):
    """Class used to produce a ready-to-compile .tex file containing a table
    from a pandas.DataFrame object. Can also compile the .tex to produce a.

    .pdf. Handles using additional latex packages. The given DataFrame is
    copied so any modification of the said DataFrame after instensiation of
    the TableWriter object has no effect on the TableWriter object,
    and vice-versa.

    This class uses pandas.DataFrame.to_latex and adds some more options to
    produce a .pdf by itself. Any option that must be given to the to_latex
    method can be given to the TableWriter through the to_latex_args argument.

    If you want to modify the DataFrame contained in the TableWriter object,
    use get_data to get a deepcopy of the DataFrame, modify the DataFrame,
    then reset it to TableWriter using set_data.
    """

    # //////////////////
    # // Initialisers //
    # //////////////////

    def __init__(
        self,
        data: pd.DataFrame = pd.DataFrame(),
        to_latex_args: Dict[str, Any] = None,
        path: Union[str, Path] = None,
        label: str = None,
        caption: str = None,
        packages: Dict[str, Dict[str, str]] = None,
        read_args: Dict = None,
        paperwidth: Union[int, float] = 0,
        paperheight: Union[int, float] = 0,
        number: int = 1,
        hide_numbering: bool = False,
    ):
        """All parameters are optionnal and can be modified by dedicated
        setters.

        Parameters ---------- data: pd.DataFrame Data to transform to table
        to_latex_args: Dict[str, Any] Dict of arguments to give to the
        DataFrame.to_latex method. See valid arguments at
        https://pandas.pydata.org/pandas-docs/stable/reference/api
        /pandas.DataFrame.to_latex.html path: Union[str, Path] Path to the
        .tex file to create label: str Label to use for the table (callable
        by LateX's \\ref) caption: str Caption to use for the table
        packages: Dict[str, Dict[str, str]] Packages to use. Keys of first
        dict are the package names. values are dict of option: value options
        to use with the package. Can be empty if no options are to be
        specified. read_args: Dict Dict of argument to pass to the read_csv
        or read_excel method. Must contain at least \"filepath_or_buffer\" (
        for a csv) or \"oi\" (for an excel) argument. paperwidth: Union[int,
        float] Width of the output table in the pdf paperheight: Union[int,
        float] Height of the page of the output pdf. If table is too long to
        fit on the page, it will be split in several pages using longtable
        package. number: int Number LateX should show after \"Table\".
        Default is 1. hide_numbering: bool Do not show \"Table N\" in the
        caption.
        """

        if read_args is None:
            read_args = {}
        if packages is None:
            packages = {}
        if to_latex_args is None:
            to_latex_args = {}

        self.__header = ""
        self.__body = "\\begin{document}\\end{document}"
        self.__footer = ""

        self.__data = data
        self.__to_latex_args = to_latex_args
        self.__path = path
        self.__label = label
        self.__caption = caption
        self.__packages = packages

        self.__paperwidth = paperwidth
        self.__paperheight = paperheight
        self.__number = number
        self.__hide_numbering = hide_numbering

        self.__special_char = ["_", "^", "%", "&"]

        if self.__data is not None and not isinstance(self.__data, pd.DataFrame):
            raise ValueError("Data must be a DataFrame")

        if not isinstance(self.__number, str):
            self.__number = str(int(self.__number))
        if self.__path is not None:
            if not isinstance(self.__path, Path):
                self.__path = Path(self.__path)
            if self.__path.suffix != ".tex":
                self.__path = self.__path.with_suffix(".tex")

        if len(read_args) > 0:
            self.load_from_file(read_args)

    @property
    def header(self):
        return self.__header

    @property
    def body(self):
        return self.__body

    @property
    def footer(self):
        return self.__footer

    def load_from_file(self, read_args: Dict) -> None:
        """Loads a table from a .csv or a .excel file.

        Parameters
        ----------
        read_args: Dict
            Arguments to pass to the read_csv or read_excel method.

        Returns
        -------
        None
        """

        if "path" in read_args:
            path = Path(read_args["path"])
            if path.suffix == ".csv":
                read_args["filepath_or_buffer"] = path
            elif path.suffix == ".xslx":
                read_args["io"] = path
            else:
                raise ValueError("Unkown extension " + path.suffix)
            del read_args["path"]

        if "filepath_or_buffer" in read_args:
            path = read_args["filepath_or_buffer"]
            if not isinstance(path, Path):
                path = Path(path)
            if not path.is_file():
                raise ValueError(str(path) + " file not found.")
            self.__data = pd.read_csv(**read_args)
        elif "io" in read_args:
            path = read_args["io"]
            if not isinstance(path, Path):
                path = Path(path)
            if not path.is_file():
                raise ValueError(str(path) + " file not found.")
            self.__data = pd.read_excel(**read_args)
        else:
            raise ValueError('"filepath_or_buffer" (for a csv) or "io"' " (for an excel) must be in read_args")

    # /////////////
    # // Setters //
    # /////////////

    def set_data(self, data: pd.DataFrame) -> None:
        """Set content of the table.

        Parameters
        ----------
        data : pd.DataFrame

        Returns
        -------
        None
        """
        if not isinstance(self.__data, pd.DataFrame):
            raise ValueError('Argument "data" must be a pandas.DataFrame object.')
        self.__data = data

    def set_to_latex_args(self, args: Dict[str, Any]) -> None:
        """Set content of to_latex_args.

        Parameters
        ----------
        args : Dict[str, Any]

        Returns
        -------
        None
        """
        self.__to_latex_args = args

    def set_path(self, path: Union[str, Path]) -> None:
        """Set output file path. Will change extension to .tex.

        Parameters
        ----------
        path : Union[str, Path]

        Returns
        -------
        None
        """
        if not isinstance(path, Path):
            path = Path(path)
        if path.suffix != ".tex":
            path = path.with_suffix(".tex")
        self.__path = path

    def set_label(self, label: str) -> None:
        """Set the table label.

        Parameters
        ----------
        label : str

        Returns
        -------
        None
        """
        self.__label = label

    def set_caption(self, caption: str) -> None:
        """Set the table caption.

        Parameters
        ----------
        caption : str

        Returns
        -------
        None
        """
        self.__caption = caption

    def set_packages(self, packages: Dict[str, Dict[str, str]]) -> None:
        """Set the dict of packages. Keys of the outer dict are the packages
        names. the outer dict values are innter dicts. Keys of those inner
        dicts are the package options names, and their inner values are the
        option values if any (None if option does not need a value)

        Parameters
        ----------
        packages : Dict[str, Dict[str, str]]

        Returns
        -------
        None
        """
        self.__packages = packages

    def set_paperwidth(self, pw: Union[int, float]) -> None:
        """Set the paper width.

        Parameters
        ----------
        pw : Union[int, float]

        Returns
        -------
        None
        """
        self.__paperwidth = pw

    def set_paperheight(self, ph: Union[int, float]) -> None:
        """Set the paper height.

        Parameters
        ----------
        ph : Union[int, float]

        Returns
        -------
        None
        """
        self.__paperheight = ph

    def set_number(self, n: Union[str, int]) -> None:
        """Set the table number (Will display "Table n:" before caption).

        Parameters
        ----------
        n : Union[str, int]

        Returns
        -------
        None
        """
        self.__number = n
        if not isinstance(self.__number, str):
            self.__number = str(int(self.__number))

    def set_hide_numbering(self, hn: bool) -> None:
        """Whether to hide the table numbering or not.

        Parameters
        ----------
        hn : bool

        Returns
        -------
        None
        """
        self.__hide_numbering = hn

    def add_to_latex_arg(self, arg: str, value: Any) -> None:
        """Adds a key (argument, value) to the list of args to pass to
        pd.to_latex.

        Parameters
        ----------
        arg: str
        value: Any

        Returns
        -------
        """
        self.__to_latex_args[arg] = value

    def add_package(self, package: str, options: Dict[str, str]) -> None:
        """Adds a key (argument, {options:values}) to the list of packages.

        Parameters
        ----------
        package: str
        options: Dict[str, str]

        Returns
        -------
        """
        self.__packages[package] = options

    # /////////////
    # // Getters //
    # /////////////

    @property
    def data(self) -> pd.DataFrame:
        return deepcopy(self.__data)

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def label(self) -> str:
        return self.__label

    @property
    def caption(self) -> str:
        return self.__caption

    @property
    def to_latex_args(self) -> Dict[str, Any]:
        return deepcopy(self.__to_latex_args)

    @property
    def packages(self) -> Dict[str, Dict[str, str]]:
        return deepcopy(self.__packages)

    @property
    def paperwidth(self) -> int:
        return self.__paperwidth

    @property
    def paperheight(self) -> int:
        return self.__paperheight

    @property
    def number(self) -> str:
        return self.__number

    @property
    def hide_numbering(self) -> bool:
        return self.__hide_numbering

    # ////////////
    # // Makers //
    # ////////////

    def _make_header(self) -> None:
        """Makes the header of the tex file."""

        # Try to guess a kind of optimal width for the table
        if self.__paperwidth == 0 and not self.__data.empty:
            charswidth = (
                len("".join(list(self.__data.columns.dropna().astype(str))))
                + max([len(ind) for ind in self.__data.index.dropna().astype(str)])
            ) * 0.178
            self.__paperwidth = charswidth + 0.8 * (len(self.__data.columns)) + 1
            if self.__paperwidth < 9:
                self.__paperwidth = 9
        # Same for height
        if self.__paperheight == 0 and not self.__data.empty:
            self.__paperheight = 3.5 + (len(self.__data.index)) * 0.45
            if self.__paperheight < 4:
                self.__paperheight = 4
            if self.__paperheight > 24:
                # Limit page height to A4's 24 cm
                self.__paperheight = 24

        self.__header = "\\documentclass{article}\n"
        self.__header += (
            "\\usepackage[margin=0.5cm, paperwidth="
            + str(self.__paperwidth)
            + "cm, paperheight="
            + str(self.__paperheight)
            + "cm]{geometry}\n"
        )
        self.__header += "\\usepackage{caption}\n"

        lt = True
        if "longtable" in self.__to_latex_args:
            lt = self.__to_latex_args["longtable"]
        else:
            self.__to_latex_args["longtable"] = True
        if lt:
            self.__header += "\\usepackage{longtable}\n"

        self.__header += (
            "\\usepackage[dvipsnames]{xcolor}\n" + "\\usepackage{booktabs}\n" + "\\usepackage[utf8]{inputenc}\n"
        )

        # Add specified packages if any
        for p in self.__packages:
            if len(self.__packages[p]) == 0:
                self.__header += "\\usepackage{" + p + "}\n"
            else:
                self.__header += "\\usepackage["
                for o in self.__packages[p]:
                    if self.__packages[p][o] is None:
                        self.__header += o + ","

                    else:
                        self.__header += o + "=" + self.__packages[p][o] + ","
                self.__header = self.__header[:-1] + "]{" + p + "}\n"
        self.__header += "\\begin{document}\n\\nonstopmode\n\\setcounter{table}{" + self.__number + "}\n"

    def _make_body(self) -> None:
        """Makes the main body of tex file."""

        if "column_format" not in self.__to_latex_args:
            self.__to_latex_args["column_format"] = "|l|" + len(self.__data.columns) * "c" + "|"

        # Needed if you do not want long names to be truncated with "..."
        # by pandas, giving bullshit results in the .tex file
        def_max_col = pd.get_option("display.max_colwidth")
        # TODO(qlieumont): pandas version
        if pd.__version__.split(".")[0] == "0":
            # pandas is older than 1.0.0
            pd.set_option("display.max_colwidth", -1)
        else:
            # pandas is 1.0.0 or newer
            pd.set_option("display.max_colwidth", None)

        if self.__data.empty:
            self.__body = self.__caption + ": Empty Dataframe\n"
            return
        else:
            self.__body = self.__data.to_latex(**self.__to_latex_args)
        pd.set_option("display.max_colwidth", def_max_col)

        append_newline = False
        if self.__caption is not None:
            in_table = self.__body.find("\\toprule")
            pre_table = self.__body[:in_table]
            post_table = self.__body[in_table:]
            if not self.__hide_numbering:
                pre_table += "\\caption{" + self.__caption + "}\n"
            else:
                pre_table += "\\caption*{" + self.__caption + "}\n"
            self.__body = pre_table + post_table
            append_newline = True

        if self.__label is not None:
            in_table = self.__body.find("\\toprule")
            pre_table = self.__body[:in_table]
            post_table = self.__body[in_table:]
            pre_table += "\\label{" + self.__label + "}\n"
            self.__body = pre_table + post_table
            append_newline = True

        if append_newline:
            self.__body = self.__body.replace("\n\\toprule", "\\\\\n\\toprule")

    def _make_footer(self) -> None:
        """Makes the footer of tex file."""

        self.__footer = "\\end{document}\n"

    def _escape_special_chars(self, s: T) -> T:
        """Will add '\\' before special characters outside of mathmode to given
        string.

        Parameters
        ----------
        s: T
            If s is not a string, will return it without changing anything

        Returns
        -------
        T
            String with special char escaped, or unmodified non-string object
        """

        if not isinstance(s, str):
            return s
        in_math = False
        previous_c = ""
        s2 = ""
        for c in s:
            if c == "$":
                in_math = not in_math
            if in_math:
                s2 += c
                previous_c = c
                continue
            if c in self.__special_char and not previous_c == "\\":
                c = "\\" + c
            previous_c = c
            s2 += c
        return s2

    # //////////////////
    # // Output files //
    # //////////////////

    def build(self):
        """build header body and footer."""
        if "escape" in self.__to_latex_args and self.__to_latex_args["escape"]:
            self.__data.index = [self._escape_special_chars(s) for s in self.__data.index]
            self.__data.columns = [self._escape_special_chars(s) for s in self.__data.columns]
            self.__data = self.__data.applymap(self._escape_special_chars)
        self.__to_latex_args["escape"] = False
        self._make_header()
        self._make_body()
        self._make_footer()

    def create_tex_file(self) -> None:
        """Creates the tex file."""

        if self.__path is None:
            raise ValueError("Must specify a file path.")

        with open(self.__path, "w") as outfile:
            # escape argument only works on column names. We need to apply
            # it on entier DataFrame, so do that then set it to False
            self.build()
            outfile.write(self.__header)
            outfile.write(self.__body)
            outfile.write(self.__footer)

    # noinspection StandardShellInjection
    def compile(
        self, silenced: bool = True, recreate: bool = True, clean: bool = True, clean_tex: bool = False,
    ) -> None:
        """Compile the pdf.

        Parameters ---------- silenced: bool Will or will not print on
        terminal the pdflatex output. Default True. recreate: bool If False
        and .tex file exists, compile from it. If True, recreate the .tex
        file first. clean: bool Removes all files created by the compilation
        which are not the .tex or the .pdf file. clean_tex: bool Also
        removes the .tex file, leaving only the .pdf.

        Returns
        -------
        None
        """

        if self.__path is None:
            raise ValueError("Must specify a file path.")
        if recreate or not self.__path.is_file():
            self.create_tex_file()

        if not self.__path.is_file():
            raise ValueError(f"Tex file {self.__path} not found.")

        path_to_compile = self.__path
        if self.__path.fs_kind == "gcs":
            path_to_compile = tempfile.NamedTemporaryFile(delete=False, suffix=".tex")
            path_to_compile.close()
            self.__path.get(path_to_compile.name)
            path_to_compile = Path(path_to_compile.name, fs="local")

        command = "pdflatex -synctex=1 -interaction=nonstopmode "
        parent = path_to_compile.parent
        if parent != ".":
            command = f"{command} -output-directory=\"{parent}\""

        command = f"{command} \"{path_to_compile}\""
        if silenced:  # unix
            if os.name == "posix":
                command = f"{command} > /dev/null"
            else:  # windows
                command = f"{command} > NUL"
        x1 = os.system(command)
        time.sleep(0.5)
        x2 = os.system(command)
        time.sleep(0.5)
        x3 = os.system(command)

        if self.__path.fs_kind == "gcs":
            for path in path_to_compile.with_suffix("").glob("*"):
                path_gcs = self.__path.with_suffix(path.suffix)
                path.put(path_gcs)
                path.rm()

        if x1 != 0 or x2 != 0 or x3 != 0:
            raise ValueError("Failed to compile pdf")

        if clean:
            self.clean(clean_tex)

    def clean(self, clean_tex: bool = False) -> None:
        """Clean files produced by latex. Also remove .tex if clean_tex is
        True.

        Parameters
        ---------
        clean_tex: bool
            To also remove the .tex file

        Returns
        -------
        None
        """
        to_keep = [".pdf", ".csv", ".excel"]
        if not clean_tex:
            to_keep.append(".tex")
        files = self.__path.with_suffix("").glob("*")
        for f in files:
            if f.suffix not in to_keep:
                f.rm()


def remove_color(obj: str) -> str:
    """Remove coloration of given object.

    Parameters
    ----------
    obj: str
        The object from which to remove the color

    Return
    ------
    str
        Object without color
    """

    if LATEX_TEXT_COLOR not in obj:
        return obj
    to_find = LATEX_TEXT_COLOR
    before_color = obj[: obj.find(to_find)]
    after_color = obj[obj.find("textcolor") + 10:]
    no_color = after_color[after_color.find("{") + 1:].replace("}", "", 1)
    return before_color + no_color


def set_color(obj: Any, color: str) -> str:
    """Add color to a given object.

    Parameters
    ----------
    obj : Any
        The object to which color must be added.
    color: str
        Must be a valid LateX color string

    Return
    ------
    str
        "\\textcolor{color}{str(obj)}"
    """
    if pd.isna(obj):
        return obj
    return LATEX_TEXT_COLOR + color + "}{" + str(obj) + "}"


# noinspection PyTypeChecker
def set_color_dataframe(
    df: Union[pd.DataFrame, pd.Series], color: str, color_index: bool = False, color_columns: bool = False,
) -> Union[pd.DataFrame, pd.Series]:
    r"""Sets color for the entier DataFrame's or Series's entries.

    To change the color of some elements in the dataframe under some condition

    Parameters
    ----------
    df: Union[pd.DataFrame, pd.Series]
        The DataFrame or Series to change the colors of
    color: str
        LateX-recognized color string
        Default ''
    color_index: bool
        To color the index too
        Default False.
    color_columns: str
        To color the columns (or Series name if df is a Series) too
        Default False.
    color_index: bool
        whether to color index or not
    color_columns: bool
        whether to color columns or not

    Returns
    -------
    Union[pd.DataFrame, pd.Series]
        Colored DataFrame or Series (dtype will be str)

    Examples
    --------

    dff = dff.mask(dff < 0, TableWriter.set_color_dataframe(dff, "red"))
    dff = pd.DataFrame(columns=dff.columns, index=dff.index, data=dff.values.astype(str))
    dff = dff.mask(dff == "nan", "")
    writer = TableWriter(data=dff)

    """
    if isinstance(df, pd.DataFrame):
        df_c = df.applymap(lambda x: set_color(x, color))
    else:
        df_c = df.apply(lambda x: set_color(x, color))
    if color_index:
        df_c.index = [set_color(x, color) for x in df_c.index]
    if color_columns:
        if isinstance(df, pd.DataFrame):
            df_c.columns = [set_color(x, color) for x in df_c.columns]
        else:
            df_c.name = set_color(df_c.name, color)
    return df_c
