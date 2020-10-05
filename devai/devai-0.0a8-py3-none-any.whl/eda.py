import plotly.express as px
import plotly.graph_objects as go
import panel as pn
import seaborn as sns

pn.extension("plotly")


def prettify_text(s):
    s = s.replace("_", " ")
    return " ".join([i.capitalize() for i in s.split()])


def get_pct_na(df, col, return_count=False):
    notnas = sum(df[col].notna())
    cnt = len(df) - notnas
    outputs = (cnt / len(df),)
    if return_count:
        outputs += (cnt,)
    else:
        return outputs[0]
    return outputs


# Panel Interactive Plots
def plot_col_vals(df, col_name, normalize):
    pretty_col_name = prettify_text(col_name)
    title = pretty_col_name

    # if data is categorical
    if col_name in df.select_dtypes(exclude=["int", "float"]):
        fig = px.bar(df[col_name].value_counts(normalize=normalize))
        fig.update_layout(
            hovermode="x",
            xaxis_title=f"{pretty_col_name} Value",
            yaxis_title="Count",
            title=title,
        )
    # if not categorical
    else:
        fig = px.box(df, y=col_name, title=title)
        fig.update_layout(
            hovermode="x", xaxis_title=f"{pretty_col_name} Stats", title=title
        )

    fig.layout.autosize = True
    return pn.pane.Plotly(fig, config={"responsive": True})


def dropdown_cols(df, col=None, normalize=False):
    if col:
        assert col in df.columns, f"column {col} does not exist in data"
    col_dropdown = pn.widgets.Select(
        value=df.columns[0] if not col else col,
        options=sorted(list(df.columns)),
        name="Select Column",
    )

    @pn.interact(col_dropdown=col_dropdown)
    def _plot(col_dropdown=col_dropdown.value):
        return plot_col_vals(df, col_dropdown, normalize=False)

    return _plot


def plot_confusion_matrix(cm, labels=None, xlabel="", ylabel=""):
    """
    plots a sklearn confusion matrix
    > cm = confusion_matrix(preds,actuals)
    > plot_confusion_matrix(cm)
    """
    sns.heatmap(cm, annot=True, xticklabels=labels,
                yticklabels=labels, fmt='g',)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()
