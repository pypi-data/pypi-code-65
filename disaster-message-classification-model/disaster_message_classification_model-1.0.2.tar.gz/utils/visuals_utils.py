# credit to Prashant Saikia for the construction of this awesome function

from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go
import plotly.io as pio
from disaster_messaging_classification_model.config import config
from sqlalchemy import create_engine
import pandas as pd
import logging

mpl_logger = logging.getLogger(__name__)
mpl_logger.setLevel(logging.WARNING)


def load_data_from_db_visual(set_label="train"):
    """
        Load data from the sqlite database. 
    Args: 
        database_filepath: the path of the database file
        set_label: indicating whether this data is used for train or test
    Returns: 
        X (DataFrame): messages 
        Y (DataFrame): One-hot encoded categories
        category_names (List)
    """

    # load data from database
    database_filepath = config.DATASET_DIR / config.DATABASE_NAME
    engine = create_engine(f"sqlite:///{database_filepath}")
    df = pd.read_sql_table(config.TABLE_NAME, engine)

    # select appropriate set
    df = df[df["set_label"] == set_label]

    return df


def plotly_wordcloud(text, title):

    wc = WordCloud(
        stopwords=set(STOPWORDS),
        max_words=config.MAX_WORDS,
        max_font_size=config.MAX_FONTS,
    )
    wc.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x = []
    y = []
    for i in position_list:
        x.append(i[0])
        y.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 100)
    new_freq_list

    trace = go.Scatter(
        x=x,
        y=y,
        textfont=dict(size=new_freq_list, color=color_list),
        hoverinfo="text",
        hovertext=["{0}{1}".format(w, f) for w, f in zip(word_list, freq_list)],
        mode="text",
        text=word_list,
    )

    layout = go.Layout(
        {
            "title": title,
            "xaxis": {"showgrid": False, "showticklabels": False, "zeroline": False},
            "yaxis": {"showgrid": False, "showticklabels": False, "zeroline": False},
            "width": config.PLOT_WIDTH,
            "height": config.PLOT_HEIGHT,
        }
    )

    fig = go.Figure(data=[trace], layout=layout)

    return fig
