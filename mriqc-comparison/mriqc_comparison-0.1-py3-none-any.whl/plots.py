""" Module to handle the plotting of iqms """

import re
from pathlib import Path

import pandas as pd
from mriqc.reports import group_html

from .local_mriqc_stats import (read_iqms,
                                find_similar_iqms,
                                save_iqms_to_tsv,
                                )


def plot_iqms_from_tsv(iqms_tsv, out_html):
    """
    Generates a html report with plots of the iqms.
    It uses MRIQC's "group_html".

    Parameters
    ----------
    iqms_tsv : Path or str
        path to the tsv file containing the Image Quality Metrics
    out_html : Path or str
        path for the html report to be generated
    """
    # get modality:
    iqms = pd.read_csv(iqms_tsv, index_col=False, sep="\t", nrows=1)
    mod = iqms['bids_meta.modality'].values[0]
    output_dir = Path(out_html).parent

    group_html(
        Path(iqms_tsv),
        mod,
        csv_failed=output_dir / f"group_variant-failed_{mod}.csv",
        out_file=out_html,
    )


def highlight_last_points_in_plot(report_html, npoints):
    """
    Highlights the last 'npoints' element in the list of iqms in a
    group plot. It draws it in red, at twice the size as the other
    points


    Parameters
    ----------
    report_html: Path or str
        path to the html report
    npoints: int
        number of points at the bottom of the report to highlight
    """
    # read the report in as a single string:
    with open(report_html, 'r') as r:
        report = r.read()

    # regex to find where to insert it in the file:
    # we match the following expression:
    # '}' followed by 3 newlines, some blank space and "// Bean lines"
    # Group 'pre' contains up to the match, 'my_match' is the match
    # itself, 'post' contains from the match up to the end of file
    p = re.compile(r'(?P<pre>.+)'
                   r'(?P<my_match>\n\s+}\n\n\n\s+// Bean lines)'
                   r'(?P<post>.+)',
                   re.MULTILINE | re.DOTALL)
    f = p.search(report)

    # grab the whitespaces or tabs before "//" in "my_match":
    my_spaces = re.search('([ \t]+)(?=//)', f.group('my_match')).group()
    # add eight more spaces:
    my_spaces += ' ' * 4

    # code to be added:
    my_addition = f'''
for (var pt = 0; pt < {npoints}; pt++) {{
    cPlot.objs.points.pts[cPlot.objs.points.pts.length - pt - 1]
        .attr("r", dOpts.pointSize) // Make it twice as wide
    .style("fill", "rgb(255, 0, 0)")
    .style("stroke", "rgb(255, 0, 0)")
}}'''
    # add those spaces before each line we want to insert
    my_addition = re.sub('\n', '\n' + my_spaces, my_addition)

    # write back to file:
    with open(report_html, 'w') as r:
        r.write(
            f.group('pre')
            + my_addition
            + f.group('my_match')
            + f.group('post')
        )


def report_comparison_w_similar(sample_iqms, iqms_set, report_html):
    """
    Creates a report in which a sample_iqms is compared to all iqms
    from runs with similar parameters in a given iqms_set

    Parameters
    ----------
    sample_iqms: DataFrame or str or Path
        the iqms we want to compare
    iqms_set: DataFrame or str or Path
        full set of iqms in which to find similar runs
    report_html: Path or str
        file where to write the report
    """

    if isinstance(sample_iqms, str) or isinstance(sample_iqms, Path):
        sample_iqms = read_iqms(sample_iqms)
    if isinstance(iqms_set, str) or isinstance(iqms_set, Path):
        iqms_set = read_iqms(iqms_set)

    # remove any columns not present in both DataFrames (there's no
    # point in showing them  in the report):
    common_cols = set(sample_iqms.columns) & set(iqms_set.columns)
    iqms_set = iqms_set[common_cols]
    sample_iqms = sample_iqms[common_cols]

    similar_iqms = find_similar_iqms(iqms_set, sample_iqms)

    # append sample_iqms at the bottom (we can only highlight iqms
    # at the bottom) and drop potential duplicates that might
    # have already been in similar_iqms:
    similar_iqms = similar_iqms.append(sample_iqms)
    similar_iqms.drop_duplicates(subset=['provenance.md5sum'],
                                 keep='last',
                                 )

    # group_html requires iqms to have a column named 'bids_name':
    similar_iqms['bids_name'] = 'foo'

    # write DataFrame to 'tsv' file
    if not report_html.endswith('.html'):
        report_html += '.html'
    report_base = str(report_html).split('.html')[0]
    save_iqms_to_tsv(similar_iqms, report_base + '.tsv')

    # generate report based on 'tsv' file
    plot_iqms_from_tsv(report_base + '.tsv', report_html)

    # highlight last entries
    highlight_last_points_in_plot(report_html, len(sample_iqms))
