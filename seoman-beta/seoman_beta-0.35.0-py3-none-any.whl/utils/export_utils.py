from typing import Optional, Dict, Any, Union, List
from time import time
import json
import csv
from collections import OrderedDict

from pytablewriter import (
    UnicodeTableWriter,
    TsvTableWriter,
)

import typer

from halo import Halo  # type: ignore


class Export:
    def __init__(
        self, data: Dict[Any, Any] = {}, keys: List[Any] = [], values: List[Any] = []
    ) -> None:
        self.data = data
        self.keys = keys
        self.values = values

    def _flatten(self, data: Dict[Any, Any], sep="_") -> OrderedDict:

        obj = OrderedDict()

        def recurse(temp, parent_key=""):
            """
            Recursive iterator to reach everything inside data.
            """

            if isinstance(temp, list):
                for i in range(len(temp)):
                    recurse(
                        temp[i], parent_key + sep + str(i) if parent_key else str(i)
                    )
            elif isinstance(temp, dict):
                for key, value in temp.items():
                    recurse(value, parent_key + sep + key if parent_key else key)
            else:
                obj[parent_key] = temp

        recurse(data)
        return obj

    def _split_to_kv(self, data: Dict[Any, Any]) -> None:
        """
        Split data to key value pair.
        """
        if (
            data.keys().__contains__("path")
            or data.keys().__contains__("permissionLevel")
            or data.keys().__contains__("sitemap_0_path")
        ):
            """
            If data contains path, it must be a sitemap instance.
            If data contains permissionLevel, it must be sites instance.
            Else a SearchAnalytics report.
            """

            # TODO FIX SITEMAPS
            for key, value in data.items():

                if key.__contains__("_"):

                    key = key.split("_")

                    if key[0] == "sitemap":
                        if len(key) >= 4:
                            key = " ".join(
                                [key[2], key[4] if key[4] != "0" else "", key[3]]
                            )
                        else:
                            key = " ".join([key[2]])

                    else:
                        key = " ".join([key[0], key[2], key[1]])

                if key not in self.keys:
                    self.keys.append(key)

                self.values.append(value)

        else:

            for key, value in data.items():
                key = key.split("_")

                if key[0] == "responseAggregationType":
                    continue

                if key[-2] == "keys":
                    # If there are multiple keys, add key number to keys eg. [keys1, keys2]
                    key = key[-2] + key[-1]

                key = key[-1] if isinstance(key, list) else key

                if key not in self.keys:
                    self.keys.append(key)

                self.values.append(value)

    def __preprocess(self) -> None:
        """
        Preprocess the data.
        """

        self._split_to_kv(self._flatten(self.data))

    def export_to_table(self) -> None:
        """
        Export in Unicode Table format.
        """

        self.__preprocess()

        sub = len(self.keys)

        writer = UnicodeTableWriter()

        writer.table_name = "Analytics"
        writer.margin = 2

        writer.headers = self.keys
        writer.value_matrix = [
            self.values[ctr : ctr + sub] for ctr in range(0, len(self.values), sub)
        ]

        writer.write_table()

    @Halo("Exporting to JSON", spinner="dots")
    def export_to_json(self, filename: str) -> None:
        """
        Export in JSON format.
        """

        with open(filename, "w") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

        print(f"Analytics successfully created in JSON format ✅")

    @Halo("Exporting to CSV", spinner="dots")
    def export_to_csv(self, filename: str) -> None:
        """
        Export in CSV format.
        """

        self.__preprocess()

        sub = len(self.keys)

        from csv import writer

        with open(filename, "w") as file:
            csv_writer = writer(file)
            csv_writer.writerow(self.keys)
            for ctr in range(0, len(self.values), sub):
                csv_writer.writerow(self.values[ctr : ctr + sub])

        typer.secho(
            "\nAnalytics successfully created in CSV format ✅", bold=True,
        )

    @Halo("Exporting to Excel", spinner="dots")
    def export_to_excel(self, filename: str) -> None:
        """
        Export in XLSX format.
        """
        from pyexcelerate import Workbook  # type: ignore

        self.__preprocess()

        sub = len(self.keys)

        data = [self.values[ctr : ctr + sub] for ctr in range(0, len(self.values), sub)]
        data.insert(0, self.keys)

        wb = Workbook()

        ws = wb.new_sheet("Analytics", data=data)

        wb.save(filename)

        typer.secho(
            "\nAnalytics successfully created in XLSX format ✅", bold=True,
        )

    @Halo("Exporting to TSV", spinner="dots")
    def export_to_tsv(self, filename: str) -> None:
        """
        Export in TSV format.
        """

        self.__preprocess()

        sub = len(self.keys)

        writer = TsvTableWriter()

        writer.headers = self.keys
        writer.value_matrix = [
            self.values[ctr : ctr + sub] for ctr in range(0, len(self.values), sub)
        ]

        writer.dump(filename)
        typer.secho(
            "\nAnalytics successfully created in TSV format ✅", bold=True,
        )

    @Halo("Exporting to Sheets", spinner="dots")
    def export_to_sheets(self, filename: str) -> None:
        """
        Export to sheets.
        """

        from tempfile import NamedTemporaryFile
        import requests as req

        import webbrowser

        from pyexcelerate import Workbook

        self.__preprocess()

        sub = len(self.keys)

        data = [self.values[ctr : ctr + sub] for ctr in range(0, len(self.values), sub)]
        data.insert(0, self.keys)

        wb = Workbook()

        ws = wb.new_sheet("Analytics", data=data)

        file = NamedTemporaryFile(suffix=".xlsx")

        wb.save(file)

        headers = {
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "x-api-key": "W0zqcZwlSd8mC6XEmkaRC2Bfx2JxLxKgXz2RWLK1",
        }

        data = open(file.name, "rb", buffering=0)
        r = req.post(
            url=f"https://406iztkqsi.execute-api.eu-central-1.amazonaws.com/prod?filename={filename}",
            data=data,
            headers={
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "x-api-key": "W0zqcZwlSd8mC6XEmkaRC2Bfx2JxLxKgXz2RWLK1",
            },
        )

        browser_open = typer.confirm("Do you want to open sheets in your browser?")
        if browser_open:
            try:
                webbrowser.open(r.json()["sheetURL"])
            except KeyError:
                typer.secho(
                    "Something went terribly wrong!",
                    bold=True,
                    fg=typer.colors.BRIGHT_RED,
                )
        else:
            try:
                typer.secho(
                    f"Needles to say, we are little bit disappointed, here is your link:  {r.json()['sheetURL']}",
                    fg=typer.colors.BRIGHT_GREEN,
                )
            except KeyError:
                print("Something went terribly wrong!")
