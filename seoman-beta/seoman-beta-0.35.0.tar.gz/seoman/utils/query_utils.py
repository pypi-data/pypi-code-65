import typer

from seoman.utils.date_utils import process_date

from typing import List, Dict, Any

from pathlib import Path
import toml


def query_builder() -> str:
    typer.secho(
        """
    FORMATTING AND TIPS

    GENERAL FORMATTING
        [Tip] You are not supposed to answer questions if it is not [REQUIRED] 
        If you want to skip that question, just press space then enter.

    URL
        [Formatting: sc-domain:example.com or https://example.com]

    DATES
        [Formatting] Dates are in YYYY-MM-DD format.
        [Example] 23 march 2020 | 2020-03-10 | 2 weeks and 4 months ago 

    FILTERS
        [Formatting] If you want to add multiple filters split them by ',' 
        [Example] country equals FRA, device notContains tablet
        [Suggested Format] dimensions, operator, expression
    
    GRANULARITY
        Granularity specifies the frequency of the data, higher frequency means higher response time.
        You must enter a one parameter.
        [Valid Parameters] daily, twodaily, threedaily, fourdaily, fivedaily, sixdaily, weekly, twoweekly, threeweekly, monthly, twomonthly, quarterly, yearly
        [Valid Parameters] monday, tuesday, wednesday, thursday, friday, saturday, sunday, weekends, weekdays
        [Examples] If you specify 'monday' seoman returns results only from mondays between start date and end date.
        [Examples] If you specify 'fivedaily' it sends splits your date range by 5 then runs unique queries.
        if your start date is 2020-03-10 and the end date is 2020-04-10 it first sends query for 03-10 to 03-15 then 03-15 to 03-20 then merges them all.   

    DIMENSIONS
        [Valid Parameters] page, query, date, device, country | for simplicity you can type 'all' to include all of them.
    
    EXPORT TYPE
        [Valid Parameters] excel, csv, json, tsv, sheets.

    ROW LIMIT
        [Valid Parameters] Must be a number from 1 to 25000.

    START ROW 
        [Valid Parameters] Must be a non-negative number.

    """,
        fg=typer.colors.BRIGHT_GREEN,
        bold=True,
    )
    url = typer.prompt("[Required] The site's URL ")
    start_date = typer.prompt("[Required] Start date of the requested date range")
    end_date = typer.prompt("[Required] End date of the requested date range")
    dimensions = typer.prompt("Zero or more dimensions to group results by")
    filters = typer.prompt(
        "Zero or more groups of filters to apply to the dimension grouping values"
    )
    start_row = typer.prompt("Zero-based index of the first row in the response")
    row_limit = typer.prompt("The maximum number of rows to return")
    search_type = typer.prompt("The search type to filter for")
    export = typer.prompt("The export type for the results")

    query: Dict[str, Dict[str, Any]] = {"query": {}}
    all_dimensions = ["page", "query", "date", "device", "country"]

    if len(url) > 5:
        query["query"].update({"url": url})

    if start_date.strip() != "":
        query["query"].update({"start-date": process_date(start_date)})

    if end_date.strip() != "":
        query["query"].update({"end-date": process_date(end_date)})

    if dimensions.strip() != "":
        new_dimensions = [dim.strip() for dim in dimensions.split(",") if dim != ""]

        if "all" in new_dimensions:
            query["query"].update(
                {"dimensions": ["date", "page", "query", "device", "country"]}
            )

        else:
            query["query"].update(
                {
                    "dimensions": [
                        dimension
                        for dimension in new_dimensions
                        if dimension in all_dimensions
                    ]
                }
            )

    if filters.strip() != "":
        query["query"].update({"filters": [filt for filt in filters.split(",")]})

    if start_row.strip() != "" and start_row.isnumeric():
        query["query"].update({"start-row": start_row})

    if row_limit.strip() != "" and row_limit.isnumeric():
        query["query"].update({"row-limit": row_limit.strip()})

    if search_type.strip() != "":
        query["query"].update({"search-type": search_type.strip().lower()})

    if export.strip() != "":
        query["query"].update({"export-type": start_date})

    typer.secho("\nYour query is ready\n", fg=typer.colors.BRIGHT_GREEN, bold=True)

    filename = typer.prompt("Give a name to your query") + ".toml"
    folder_path = Path.home() / ".queries"
    file_path = Path.home() / ".queries" / Path(filename)

    if not Path(folder_path).exists():
        Path(folder_path).mkdir(exist_ok=False)

    if not Path(file_path).exists():
        with open(file_path, "w") as file:
            toml.dump(query, file)
    else:
        pass
        # TODO
    return f"{filename} created successfully!"


def query_deleter(filename: str) -> None:
    """
    Delete a query from queries directory.
    """

    if not filename.endswith(".toml"):
        filename = filename + ".toml"

    p = Path.home() / ".queries" / filename

    p.unlink()


def query_lister(filename: str) -> None:
    """
    Show details of the selected query.
    """

    if not filename.endswith(".toml"):
        filename = filename + ".toml"

    p = Path.home() / ".queries" / filename

    with open(str(p), "r") as file:
        query_file = file.read()

    print(query_file)

