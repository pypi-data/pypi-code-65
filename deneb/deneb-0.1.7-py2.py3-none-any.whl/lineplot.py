from typing import Any, Dict, List, Optional, Tuple, Union

import altair as alt
import pandas as pd

from .utils import Chart


def lineplot(
    df,
    x: str,
    y: str,
    label_orient: str = "top",
    title_orient: str = "bottom",
    column: Optional[str] = None,
    column_title: str = "",
    column_sort: Optional[List[str]] = None,
    column_labels: bool = True,
    row: Optional[str] = None,
    row_title: str = "",
    row_sort: Optional[List[str]] = None,
    row_labels: bool = True,
    aggregate: Optional[str] = "mean",
    points: bool = True,
    lines: bool = True,
    errorbars: bool = True,
    error_extent: str = "stdev",
    limits: Optional[List[float]] = None,
    independent_x: bool = True,
    independent_y: bool = False,
    spacing: int = 5,
    color: Optional[Union[str, alt.Color]] = None,
    shape: Optional[Union[str, alt.Shape]] = None,
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> Chart:
    """Produces lineplot with optional errorbars and facets

    Args:
        df: Dataframe
        x: Shorthand for x
        y: Shorthand for y
        label_orient: Orientation of column labels
        title_orient: Orientation of column title
        column: Shorthand for columns (optional) which are faceted
        column_title: Title text for columns displayed 
        column_sort: Optional sorting for columns
        column_labels: Whether header labels should be displayed
        row: Shorthand for rows (optional) which are faceted
        row_title: Title text for rows displayed 
        row_sort: Optional sorting for rows
        row_labels: Whether header labels should be displayed
        aggregate: Aggregation function for y values
        points: Whether to show points
        lines: Whether to show lines
        errorbars: Whether to show errorbars
        error_extent: Extent of errorbars, e.g., stdev or stderr
        limits: Limits for y-axis
        independent_x: Whether x-axes are independent
        independent_y: Whether y-axes are independent
        spacing: Spacing between facets
        color: Colorscale
        shape: Shape encoding
        height: Height of plot in facet
        width: Width of plot in facet

    Returns:
        Chart
    """
    if color is None:
        color_kwarg = {}
    else:
        color_kwarg = {"color": color}

    if shape is None:
        shape_kwarg = {}
    else:
        shape_kwarg = {"shape": shape}

    if limits is not None:
        y_scale = alt.Scale(zero=False, domain=limits)
    else:
        y_scale = alt.Scale(zero=False)

    lines_layer = (
        alt.Chart()
        .mark_line()
        .encode(
            x=alt.X(x, title=""),
            y=alt.Y(y, scale=y_scale, aggregate=aggregate),
            **color_kwarg
        )
    )

    points_layer = (
        alt.Chart()
        .mark_point(filled=True)
        .encode(
            x=alt.X(x, title=""),
            y=alt.Y(y, scale=y_scale, aggregate=aggregate),
            **color_kwarg,
            **shape_kwarg
        )
    )

    errorbars_layer = (
        alt.Chart()
        .mark_errorbar(extent=error_extent)
        .encode(
            x=alt.X(x, title=""),
            y=alt.Y(y, scale=y_scale),
            **color_kwarg,
            **shape_kwarg
        )
    )

    layers = []
    if lines:
        layers.append(lines_layer)
    if points:
        layers.append(points_layer)
    if errorbars:
        layers.append(errorbars_layer)

    chart = alt.layer(*layers, data=df)

    if height is not None:
        chart = chart.properties(height=height)

    if width is not None:
        chart = chart.properties(width=width)

    if column is not None or row is not None:
        facet_kwargs = {
            "spacing": spacing,
        }
        if column is not None:
            facet_kwargs["column"] = alt.Column(
                column,
                title=column_title,
                header=alt.Header(labels=column_labels),
                sort=column_sort,
            )
        if row is not None:
            facet_kwargs["row"] = alt.Row(
                row,
                title=row_title,
                header=alt.Header(labels=row_labels),
                sort=row_sort,
            )
        chart = chart.facet(**facet_kwargs)

    if independent_x:
        chart = chart.resolve_scale(x="independent")

    if independent_y:
        chart = chart.resolve_scale(y="independent")

    chart = chart.configure_header(titleOrient=title_orient, labelOrient=label_orient)

    return chart
