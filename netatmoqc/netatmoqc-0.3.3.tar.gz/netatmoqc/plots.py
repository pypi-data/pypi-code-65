#!/usr/bin/env python3
import humanize
import numpy as np
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from .logs import get_logger


# This "config" is plotly's fig.show config, not our parsed config file.
# See <https://github.com/plotly/plotly.js/blob/master/src/plot_api/
#      plot_config.js>
DEF_FIGSHOW_CONFIG = dict(editable=True, displaylogo=False)


def get_obs_scattergeo_trace(df, trace_name=None, marker={}, visible=True):
    """ Get a go.Scattergeo object from observations in a dataframe df """

    base_marker = dict(
        color="blue", size=8, opacity=0.75, line=dict(width=1.0)
    )
    if marker == {}:
        marker = base_marker
    else:
        new_marker = base_marker.copy()
        new_marker.update(marker)
        marker = new_marker

    # Format popup hover text
    if trace_name is None:
        hovertemplate = []
    else:
        hovertemplate = ["<b>%s</b><br>" % (trace_name)]
    hoverinfo_cols = [c for c in df.columns if not c.startswith("_")]
    for ic, c in enumerate(hoverinfo_cols):
        fmt = None
        if pd.api.types.is_float_dtype(df[c]):
            fmt = ": .5f"
        elif pd.api.types.is_datetime64_any_dtype(df[c]):
            fmt = "| %Y-%m-%d %H:%M:%S"
        if fmt is None:
            hovertemplate.append("%s: %%{customdata[%d]}" % (c, ic))
        else:
            hovertemplate.append("%s: %%{customdata[%d]%s}" % (c, ic, fmt))
    hovertemplate = "<br>".join(hovertemplate)

    return go.Scattergeo(
        name=trace_name,
        lat=df.lat,
        lon=df.lon,
        mode="markers",
        marker=marker,
        customdata=df,
        hovertemplate=hovertemplate,
        hoverlabel=dict(namelength=0),
        visible=visible,
    )


def draw_boundaries(
    fig,
    domain,
    name="boundaries",
    corners=None,
    showlegend=True,
    legendgroup=None,
    **kwargs
):
    """ Add to fig line segments connecting the given corners within the domain

    corners needs to hold (x, y) coords of he start and end of the corners
    of the closed boundary to br drawn. If corners is not passed, then the
    domain corners will be used.

    We interpolate using (x, y) instead of (lon, lat) to prevent distorted
    line segments (segments that do not conform to the used projection).
    """
    if corners is None:
        corners = domain.domain_corners_xy

    # Construct line segments
    segments = []
    npts_per_segment = max(max(domain.nlon, domain.nlat) // 100, 5)
    for i in range(len(corners)):
        start = corners[i]
        end = corners[(i + 1) % len(corners)]
        segments.append(
            dict(
                x=np.linspace(start[0], end[0], npts_per_segment),
                y=np.linspace(start[1], end[1], npts_per_segment),
            )
        )

    xvals = np.empty(3 * len(segments) * npts_per_segment)
    yvals = np.empty(3 * len(segments) * npts_per_segment)

    # Add all segments as a single trace
    # Put start points in go.Scattergeo's "single-trace" style
    xvals[::3] = np.concatenate([s["x"] for s in segments])
    yvals[::3] = np.concatenate([s["y"] for s in segments])
    lons, lats = domain.xy2lonlat(xvals, yvals)
    # Same for end points
    lats[1::3] = np.roll(lats[::3], 1)
    lons[1::3] = np.roll(lons[::3], 1)
    # Indicate separation between traces
    lats[2::3] = None
    lons[2::3] = None

    fig.add_trace(
        go.Scattergeo(
            name=name,
            lat=lats,
            lon=lons,
            mode="lines",
            line=kwargs,
            legendgroup=legendgroup,
            showlegend=showlegend,
        )
    )

    return fig


def draw_grid_pts(
    fig, domain, display_grid_max_gsize=None, name="Grid", **marker_opts
):
    """ Add to fig a trace containing a selection of grid points """
    if display_grid_max_gsize is None:
        display_grid_max_gsize = domain.gsize
    if display_grid_max_gsize <= 0:
        return fig

    grid_draw_every = max(1, int(display_grid_max_gsize / domain.gsize))
    lons, lats = domain.get_grid_ij2lonlat_map()
    if grid_draw_every > 1:
        name += " (every %s point of)" % (humanize.ordinal(grid_draw_every))
    fig.add_trace(
        go.Scattergeo(
            name=name,
            lat=lats[::grid_draw_every, ::grid_draw_every].flatten(),
            lon=lons[::grid_draw_every, ::grid_draw_every].flatten(),
            mode="markers",
            marker=marker_opts,
        )
    )
    return fig


def get_domain_fig(
    domain,
    # Show 1 grid point every "display_grid_max_gsize" meters.
    # Don't show any grid point if display_grid_max_gsize <=0.
    display_grid_max_gsize=0,
    lonrange=None,
    latrange=None,
    ezone=None,
    obs_df=None,
    **kwargs
):
    """ Make a map representation of "domain" (a ".domains.Domain" object) """
    # Should we plot the extension zone?
    if ezone is None:
        ezone = domain.ezone > 0

    # Define longitude range
    if lonrange is None:
        if domain.nlon == 1:
            minlon = -180
            maxlon = 180
        elif ezone:
            minlon = domain.ezone_minlon
            maxlon = domain.ezone_maxlon
        else:
            minlon = domain.minlon
            maxlon = domain.maxlon
        lonrange = np.clip((minlon - 2.0, maxlon + 2.0), -180, 180)

    # Define latitude range
    if latrange is None:
        if domain.nlat == 1:
            minlat = -90
            maxlat = 90
        elif ezone:
            minlat = domain.ezone_minlat
            maxlat = domain.ezone_maxlat
        else:
            minlat = domain.minlat
            maxlat = domain.maxlat
        latrange = np.clip((minlat - 2.0, maxlat + 2.0), -90, 90)

    # Make main, base figure
    fig = go.Figure(go.Scattergeo())
    fig.update_geos(
        # resolution is either 50 (higher) or 110 (lower)
        resolution=50,
        projection_type=domain.plotly_projname,
        center=dict(lon=domain.lonc, lat=domain.latc),
        showland=True,
        showcountries=True,
    )
    fig.update_layout(
        height=800,
        margin=dict(r=0, l=0, b=0),
        title=dict(
            text="{} Domain Boundaries and Grid ({} Projection)".format(
                domain.name, domain.projname
            ),
            xanchor="center",
            x=0.5,
            yanchor="top",
            y=0.9,
        ),
        legend=dict(
            orientation="v",
            xanchor="left",
            x=1.0,
            yanchor="middle",
            y=0.5,
            # Use "reversed" instead of "normal" because we can't directly
            # conrol the order of the layers drawn next. We then draw them
            # from lower to upper and reverse the legend.
            traceorder="reversed",
        ),
        geo=dict(
            lataxis=dict(range=latrange, showgrid=True, dtick=10,),
            lonaxis=dict(range=lonrange, showgrid=True, dtick=15,),
        ),
    )

    # Draw selection of grid points
    # (a) Support grid (if used)
    if domain.thinning_grid_coarse_factor > 0:
        fig = draw_grid_pts(
            fig,
            domain.get_thinning_grid_version(),
            display_grid_max_gsize=display_grid_max_gsize,
            name="Support Grid",
            color="red",
            size=1.5,
            opacity=0.5,
        )
    # (b) Main grid
    fig = draw_grid_pts(
        fig,
        domain,
        display_grid_max_gsize=display_grid_max_gsize,
        color="black",
        size=1.5,
    )

    # Add line segments to mark domain, subdomain and extension zone boundaries
    # (a) Observations
    if obs_df is not None:
        trace = get_obs_scattergeo_trace(obs_df, trace_name="Observations")
        fig.add_trace(trace)

    # (b) Extension zone
    if ezone:
        fig = draw_boundaries(
            fig,
            domain,
            name="Extension Zone",
            corners=domain.ezone_corners_xy,
            color="blue",
            dash="dash",
        )

    # (c) Subdomain boundaries
    if domain.n_subdomains > 1:
        splits = domain.split()
        for i, subdomain in zip(range(len(splits))[::-1], splits[::-1]):
            showlegend = i == 0
            sub_name = "Subdomains"
            fig = draw_boundaries(
                fig,
                subdomain,
                name=sub_name,
                showlegend=showlegend,
                legendgroup="Subdomains",
                color="black",
                width=1,
            )

    # (d) Draw main domain doundaries
    fig = draw_boundaries(fig, domain, name="Domain", color="red")

    return fig


def make_clustering_fig(df, domain, **kwargs):
    """ Make fig produced by/in "clustering" command/app """

    # Make sure df index is sequential
    df = df.reset_index(drop=True)

    if not "cluster_label" in df.columns:
        df["cluster_label"] = np.nan
    if not "original_cluster_label" in df.columns:
        df["original_cluster_label"] = df["cluster_label"]

    # Add a col to df with descriptive labels for plot
    label_counts = df["cluster_label"].value_counts()
    orig_label_counts = df["original_cluster_label"].value_counts()
    # Vectorize setting of plot labels. About 25x faster than looping over df.
    def _set_plot_label(label, orig_label):
        if label == -1:
            # Obs removed in the normal way with clustering
            legend_label = "Rejected: "
            label_count = label_counts[label]
        elif label == -2:
            # Outliers found after main clustering
            legend_label = "Cluster {}, outliers:".format(orig_label)
            label_count = (
                orig_label_counts[orig_label] - label_counts[orig_label]
            )
        elif label == -3:
            legend_label = "Outliers, preliminary clustering:"
            label_count = label_counts[label]
        elif label == -4:
            legend_label = "Missed (due to domain splitting):"
            label_count = label_counts[label]
        elif label == -5:
            legend_label = "Moving stations:"
            label_count = label_counts[label]
        else:
            legend_label = "Cluster {}, accepted:".format(int(label))
            label_count = label_counts[label]
        legend_label += " {} obs".format(int(label_count))
        return legend_label

    set_plot_label = np.vectorize(_set_plot_label, otypes=[str])
    df["_plot_label"] = set_plot_label(
        df["cluster_label"], df["original_cluster_label"]
    )

    # Define colours to be used in the plot
    # See colorscales at <https://plotly.com/python/builtin-colorscales>
    color_discrete_sequence = [
        px.colors.qualitative.Light24,
        px.colors.qualitative.Alphabet,
        px.colors.qualitative.Dark24,
    ][0]

    # Define symbols to be used in the plot
    # See all symbols at
    # <https://plotly.com/python/marker-style/#custom-marker-symbols>
    symbols = [
        "circle",
        "octagon",
        "hexagon2",
        "circle-dot",
        "octagon-dot",
        "circle-cross",
        "circle-x",
    ]

    # Now assign appropriate colors and symbols to each observation row
    unique_labels = df["cluster_label"].unique()
    label2color_map = dict()
    label2symbol_map = dict()
    for i, label in enumerate(unique_labels[unique_labels > -1]):
        color = color_discrete_sequence[i % len(color_discrete_sequence)]
        symbol = symbols[(i // len(color_discrete_sequence)) % len(symbols)]
        label2color_map[label] = color
        label2symbol_map[label] = symbol

    def _label2symbol(label):
        if label < 0:
            return "x-open"
        else:
            return label2symbol_map[label]

    label2symbol = np.vectorize(_label2symbol, otypes=[str])

    def _label2color(label):
        if label < 0:
            return "black"
        else:
            return label2color_map[label]

    label2color = np.vectorize(_label2color, otypes=[str])

    df["_plot_color"] = label2color(df["original_cluster_label"])
    df["_plot_symbol"] = label2symbol(df["cluster_label"])

    #########################
    # Now create the figure #
    #########################

    fig = domain.get_fig(max_ngrid=0, **kwargs)
    fig.update_layout(
        height=600,
        clickmode="event+select",
        title=None,
        margin=dict(r=0, l=0, b=0, t=0),
        legend_title="<b>Clustering of Observations</b>",
        legend_traceorder="normal",
    )

    # Add each group as a different trace
    for label, cluster_df in df.groupby("_plot_label", sort=False):

        marker = dict(
            color=cluster_df["_plot_color"].iloc[0],
            symbol=cluster_df["_plot_symbol"].iloc[0],
        )

        if cluster_df["cluster_label"].iloc[0] < 0:
            trace_visible = "legendonly"
            marker.update(dict(size=5, opacity=0.25))
        else:
            trace_visible = True

        trace = get_obs_scattergeo_trace(
            cluster_df, trace_name=label, marker=marker, visible=trace_visible,
        )
        fig.add_trace(trace)

    return fig


def show_cmd_get_fig_from_dataframes(args, dataframes, domain):
    """ Make fig produced by "show" command """

    logger = get_logger(__name__, args.loglevel)

    fig = domain.get_fig(max_ngrid=0)
    fig.update_layout(
        title=dict(
            text="NetatmoQC Output",
            xanchor="center",
            x=0.5,
            yanchor="top",
            y=0.9,
        ),
        margin=dict(r=0, l=0, b=0),
    )

    # We'll use a fig dict so we can control the order in which data is added
    fig_dict = fig.to_dict()

    new_fig_data = []
    # Add contents from each file as a different trace
    for fname, df in dataframes.items():
        logger.info("Add data from file '%s' (%d obs)", fname, len(df.index))
        if "accepted" in fname:
            trace_visible = True
            marker = dict(color="blue")
        else:
            trace_visible = "legendonly"
            marker = dict(size=5, opacity=0.25, symbol="x-open")
            if "moving" in fname:
                marker["color"] = "red"
            else:
                marker["color"] = "black"

        trace_name = Path(fname).stem.replace("_", " ").title()
        trace_name += " (%d obs)" % (len(df.index))
        trace = get_obs_scattergeo_trace(
            df, trace_name=trace_name, marker=marker, visible=trace_visible
        )
        new_fig_data.append(trace)

    # Add data in reverse order. Needed for legend/layer order.
    fig_dict["data"] = new_fig_data[::-1] + fig_dict["data"]
    return go.Figure(fig_dict)


###########################################################
# Routines only used in apps/scattergeo_timeseries/app.py #
###########################################################


# For animations, see:
# <https://plotly.com/python/animations/#animated-figures-with-graph-objects>
def generate_single_frame(df, dataset_var, frame_duration, frame={}):
    """ Generate a single frame of teh animation produced by scattergeo app """

    # Controlling colour schemes
    if dataset_var in ["temperature"]:
        color_scale = px.colors.diverging.RdBu_r
    else:
        color_scale = px.colors.sequential.haline_r

    marker = dict(
        color=df[dataset_var],
        colorscale=color_scale,
        opacity=0.5,
        line=dict(color="black", width=0.25),
        colorbar=dict(
            titleside="right", ticks="outside", showticksuffix="last",
        ),
    )
    trace = get_obs_scattergeo_trace(df, marker=marker)
    frame["data"] = trace

    slider_step = dict(
        args=[
            [frame["name"]],
            dict(
                frame=dict(duration=frame_duration, redraw=True),
                mode="immediate",
                transition=dict(duration=frame_duration),
            ),
        ],
        label=frame["name"],
        method="animate",
    )

    return frame, slider_step


def init_fig_dict(domain, dataset_var, frame_duration):
    """ Initiate dict used to instantiate plotly fig used in scattergeo app

    We make the figure by constructing a dictionary and passing it to the final
    plotly method.
    """

    fig = domain.get_fig(max_ngrid=0)
    fig.update_geos(resolution=110)
    fig_dict = fig.to_dict()
    # resolution is either 50 (higher) or 110 (lower)
    fig_dict["frames"] = []

    # Figure layout
    fig_dict["layout"]["title"]["text"] = "NetAtmo Data: {}".format(
        dataset_var
    )

    fig_dict["layout"]["updatemenus"] = [
        # <https://plotly.com/python/reference/layout/updatemenus>
        dict(
            type="buttons",
            direction="left",
            showactive=False,
            xanchor="right",
            yanchor="top",
            x=0.1,
            y=0,
            pad=dict(r=10, t=87),
            buttons=[
                dict(
                    label="Play",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(duration=frame_duration, redraw=True,),
                            fromcurrent=True,
                            transition=dict(
                                duration=frame_duration / 2,
                                easing="cubic-in-out",
                            ),
                        ),
                    ],
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(duration=0, redraw=True),
                            mode="immediate",
                            transition=dict(duration=0),
                        ),
                    ],
                ),
            ],
        )
    ]

    sliders_dict = dict(
        active=0,
        len=0.9,
        yanchor="top",
        xanchor="left",
        x=0.1,
        y=0,
        pad=dict(b=10, t=50),
        currentvalue=dict(
            font=dict(size=20), prefix="DTG: ", visible=True, xanchor="right",
        ),
        transition=dict(duration=frame_duration / 2, easing="cubic-in-out",),
        steps=[],
    )

    return fig_dict, sliders_dict
