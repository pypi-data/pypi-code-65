import numpy as np
import matplotlib as mpl
from matplotlib.backends import backend_svg
import matplotlib.pyplot as plt
import seaborn as sns
import numbers
import io

def plot_colored_line(t, x, y, cmap='viridis', linewidth=3, ax=None,
                      colorbar=True):
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = mpl.collections.LineCollection(segments, cmap=plt.get_cmap(cmap))
    lc.set_array(t) # Collection is a ScalarMappable
    lc.set_linewidth(linewidth)

    if ax is None:
        fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.set_xlim(get_lim(x))
    ax.set_ylim(get_lim(y))

    if colorbar:
        cnorm = mpl.colors.Normalize(vmin=np.min(t), vmax=np.max(t))
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=cnorm)
        sm.set_array(t)
        # can't find a way to set a colorbar simply without grabbing the
        # current axis, so make sure we can restore what the "current axis"
        # was before we did this
        cax = plt.gca()
        plt.sca(ax)
        cbar = plt.colorbar(sm)
        plt.sca(cax)
    return ax

def get_lim(x, margin=0.1):
    min = np.min(x)
    max = np.max(x)
    dx = max - min
    return [min - margin*dx, max + margin*dx]


def cmap_from_list(labels, palette=None, log=False, vmin=None, vmax=None):
    # sequential colormap if numbers
    if isinstance(labels[0], numbers.Number):
        labels = np.array(labels)
        if vmin is None:
            vmin = labels.min()
        if vmax is None:
            vmax = labels.max()
        if log:
            cnorm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
        else:
            cnorm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        if palette is None:
            palette = 'viridis'
        cmap = mpl.cm.get_cmap(palette)
        return lambda l: cmap(cnorm(l))
    # otherwise categorical map
    else:
        if log:
            raise ValueError('LogNorm makes no sense for categorical labels.')
        labels = list(set(labels))
        n_labels = len(labels)
        pal = sns.color_palette(palette, n_colors=n_labels)
        cmap = {labels[i]: pal[i] for i in range(n_labels)}
        return lambda l: cmap[l]

def draw_triangle(alpha, x0, width, orientation, base=10,
                            **kwargs):
    """Draw a triangle showing the best-fit slope on a linear scale.

    Parameters
    ----------
    alpha : float
        the slope being demonstrated
    x0 : (2,) array_like
        the "left tip" of the triangle, where the hypotenuse starts
    width : float
        horizontal size
    orientation : string
        'up' or 'down', control which way the triangle's right angle "points"
    base : float
        scale "width" for non-base 10

    Returns
    -------
    corner : (2,) np.array
        coordinates of the right-angled corner of the triangle
    """
    x0, y0 = x0
    x1 = x0 + width
    y1 = y0 + alpha*(x1 - x0)
    plt.plot([x0, x1], [y0, y1], 'k')
    if (alpha >= 0 and orientation == 'up') \
    or (alpha < 0 and orientation == 'down'):
        plt.plot([x0, x1], [y1, y1], 'k')
        plt.plot([x0, x0], [y0, y1], 'k')
        # plt.plot lines have nice rounded caps
        # plt.hlines(y1, x0, x1, **kwargs)
        # plt.vlines(x0, y0, y1, **kwargs)
        corner = [x0, y1]
    elif (alpha >= 0 and orientation == 'down') \
    or (alpha < 0 and orientation == 'up'):
        plt.plot([x0, x1], [y0, y0], 'k')
        plt.plot([x1, x1], [y0, y1], 'k')
        # plt.hlines(y0, x0, x1, **kwargs)
        # plt.vlines(x1, y0, y1, **kwargs)
        corner = [x1, y0]
    else:
        raise ValueError(r"Need $\alpha\in\mathbb{R} and orientation\in{'up', 'down'}")
    return corner

def draw_power_law_triangle(alpha, x0, width, orientation, base=10,
                            x0_logscale=True, label=None,
                            label_padding=0.1, text_args={}, **kwargs):
    """Draw a triangle showing the best-fit power-law on a log-log scale.

    Parameters
    ----------
    alpha : float
        the power-law slope being demonstrated
    x0 : (2,) array_like
        the "left tip" of the power law triangle, where the hypotenuse starts
        (in log units, to be consistent with draw_triangle)
    width : float
        horizontal size in number of major log ticks (default base-10)
    orientation : string
        'up' or 'down', control which way the triangle's right angle "points"
    base : float
        scale "width" for non-base 10

    Returns
    -------
    corner : (2,) np.array
        coordinates of the right-angled corhow to get text outline matplotlibner of the triangle
    """
    if x0_logscale:
        x0, y0 = [base**x for x in x0]
    else:
        x0, y0 = x0
    x1 = x0*base**width
    y1 = y0*(x1/x0)**alpha
    plt.plot([x0, x1], [y0, y1], 'k')
    if (alpha >= 0 and orientation == 'up') \
    or (alpha < 0 and orientation == 'down'):
        plt.plot([x0, x1], [y1, y1], 'k')
        plt.plot([x0, x0], [y0, y1], 'k')
        # plt.plot lines have nice rounded caps
        # plt.hlines(y1, x0, x1, **kwargs)
        # plt.vlines(x0, y0, y1, **kwargs)
        corner = [x0, y1]
    elif (alpha >= 0 and orientation == 'down') \
    or (alpha < 0 and orientation == 'up'):
        plt.plot([x0, x1], [y0, y0], 'k')
        plt.plot([x1, x1], [y0, y1], 'k')
        # plt.hlines(y0, x0, x1, **kwargs)
        # plt.vlines(x1, y0, y1, **kwargs)
        corner = [x1, y0]
    else:
        raise ValueError(r"Need $\alpha\in\mathbb{R} and orientation\in{'up', 'down'}")
    if label is not None:
        xlabel = x0*base**(width/2)
        ylabel = y1*base**label_padding if orientation == 'up' else y0*base**(-label_padding)
        plt.text(xlabel, ylabel, label, horizontalalignment='center',
                 verticalalignment='center', **text_args)
    return corner


def set_ax_size(w, h, ax=None):
    """pass absolute height of axes, not figure

    gets around fact that throughout matplotlib, only full figure aspect ratio
    is under user control.

    w, h: width, height in inches """
    if not ax: ax=plt.gca()
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    ax.figure.set_size_inches(figw, figh)


import numbers
import io
def make_at_aspect(plot_funcs, heights, col_width,  tight_width='bbox',
                   hspace=None, halign=None, is_ratio=True, **kw_figs):
    """Figure with fixed column width and requested aspect ratios per subplot.

    Parameters
    ----------
    plot_funcs : Sequence[Callable[[matplotlib.axes.Axes], None]]
        function to create each subplot given the axes to draw it into
    heights : float or Sequence[float]
        If is_ratio is True, this is the height/width ratio desired for each
        subplot. A single number is allowed for fixed aspect ratio across all
        axes.  If is_ratio is False, this is the absolute height desired.
    col_width : float
        absolute width of figure desired, in inches
    tight_width : string
        'bbox' or 'tight'. 'bbox' means use default generated by
        bbox_inches='tight'. 'tight' means to actually remove all whitespace
        from left and right size of final figure. This option is more a
        reflection of my lack of interest in figuring out which of these is the
        "correct" thing to do as opposed to actually useful.
    hspace : float
        vertical space between adjacent axes bboxes as fraction of average axis
        height (not fraction of average axis bbox height). defaults to value in
        rc (fig.subplotpars.hspace).
    halign : {'min_axis_width', 'full'} or Sequence[string]
        'full' means make each axis as wide as it can be while still fitting in
        the figure boundary. 'min_axis_width' means make the final axis width
        match the width of the smallest axis (so that multiple axes with
        different amounts of required label padding still line up).
    is_ratio : bool or Sequence[bool]
        Whether each height request is a ratio or absolute axis height desired.


    Returns
    -------
    ax : matplotlib.figure.Figure
        the final figure

    Notes
    -----
    No extra "axes_kw" argument is provided, since each axis is passed to it's appropriate
    plot_func, which should be able to set any relevant extra parameters for that axis.
    """
    n_plots = len(plot_funcs)
    if halign is None:
        halign = n_plots * ['min_axis_width']
    try:
        if n_plots != len(heights):
            raise ValueError("length of heights and plot_funcs should match")
    except TypeError: # no __len__
        if not isinstance(heights, numbers.Number):
            raise ValueError("heights should be list of ratios or single float")
        # we have a single number, simply tile it accordingly
        heights = n_plots*[heights]
    heights = np.array(heights)
    # also tile is_ratio if needed
    if isinstance(is_ratio, bool):
        is_ratio = n_plots*[is_ratio]
    is_ratio = np.array(is_ratio)

    # first make "test" figure to get correct extents including all labels, etc
    # leave a 2x margin of error for the labels to fit into vertically.
    max_heights = heights.copy()
    max_heights[is_ratio] = heights[is_ratio]*col_width
    test_fig_height = 2*np.sum(max_heights)
    fig, axs = plt.subplots(nrows=n_plots, figsize=(col_width, test_fig_height), **kw_figs)
    if n_plots == 1:
        axs = [axs] # not sure why the inconsistency in subplots interface...
    for i in range(n_plots):
        plot_funcs[i](axs[i])

    # "dry-run" a figure save to get "real" bbox for full figure with all children
    fig.canvas = backend_svg.FigureCanvasSVG(fig)
    preprint = fig.canvas.print_svg(io.BytesIO(), dpi=300, facecolor=[1,1,1], edgecolor=[0,0,0],
                          orientation='portrait', dryrun=True)
    #TODO: which is right? neither seem exactly right according to inkscape?
    # if we use fig.canvas.renderer instead, we get different answers o.o
    renderer = fig._cachedRenderer
    disp_to_inch = fig.dpi_scale_trans.inverted()
    fig_to_inch = fig.dpi_scale_trans.inverted() + fig.transFigure

    # now get extents of axes themselves and axis "bbox"s (i.e. including labels, etc)
    ax_bbox_inches = []
    ax_inches = []
    for ax in axs:
        ax_bbox = ax.get_tightbbox(renderer) # docs say in "figure pixels", but means "display"
        ax_bbox_inches.append(disp_to_inch.transform(ax_bbox))
        ax_inches.append(fig_to_inch.transform(ax.get_position()))
    x0s, y0s, x1s, y1s = map(np.array, zip(*map(np.ndarray.flatten, ax_bbox_inches)))
    ax0s, ay0s, ax1s, ay1s = map(np.array, zip(*map(np.ndarray.flatten, ax_inches)))

    # get final horizontal size of figure
    if tight_width == 'bbox':
        bbox_inches = fig.get_tightbbox(renderer).bounds
        real_h_extents = [bbox_inches[0], bbox_inches[2]]
        real_v_extents = [bbox_inches[1], bbox_inches[3]]
    elif tight_width == 'tight':
        real_h_extents = [np.min(x0s), np.max(x1s)]
        real_v_extents = [np.min(y0s), np.max(y1s)]

    # calculate space required in addition to axes themselves
    pads_left = ax0s - x0s
    pads_right = x1s - ax1s
    pads_above = y1s - ay1s
    pads_below = ay0s - y0s
    max_pad_left = np.max(pads_left)
    max_pad_right = np.max(pads_right)

    # get axes sizes
    x0 = np.zeros(n_plots)
    x1 = np.zeros(n_plots)
    for i in range(n_plots):
        if halign[i] == 'full':
            x0[i] = pads_left[i]
            x1[i] = col_width - pads_right[i]
        elif halign[i] == 'min_axis_width':
            x0[i] = max_pad_left
            x1[i] = col_width - max_pad_right
        else:
            raise ValueError(f"Invalid option passed for halign: {halign[i]}. "
                              "Should be 'full' or 'min_axis_width'")
    real_heights = heights.copy()
    real_heights[is_ratio] = heights[is_ratio]*(x1 - x0)[is_ratio]
    if hspace is None:
        hspace = fig.subplotpars.hspace
    hspace = hspace*np.mean(real_heights)

    # make new figure with axes "correctly" located
    total_height = np.sum(real_heights) + np.sum(pads_below) \
            + np.sum(pads_above) + (n_plots - 1)*hspace
    fig = plt.figure(figsize=(col_width, total_height), **kw_figs)
    cur_y = 1 # track y pos normalized to height of figure
    for i in range(n_plots):
        left = x0[i]/col_width
        right = x1[i]/col_width
        cur_y -= pads_above[i]/total_height
        top = cur_y
        cur_y -= real_heights[i]/total_height
        bottom = cur_y
        cur_y -= pads_below[i]/total_height
        cur_y -= hspace/total_height
        #TODO if right - left < 0, or top - bottom < 0, complain that an
        # annotation that has been requested doesn't fit in the column
        # absolutely
        ax = fig.add_axes([left, bottom, right - left, top-bottom])
        plot_funcs[i](ax)
    return fig, real_heights
