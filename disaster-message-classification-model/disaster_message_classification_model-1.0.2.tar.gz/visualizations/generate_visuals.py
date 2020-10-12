import plotly
from disaster_messaging_classification_model.utils.visuals_utils import (
    plotly_wordcloud,
    load_data_from_db_visual,
)
import string, json


class VisualsGeneration:
    """" module that generates the plotly visualizations """

    def __init__(self):
        self.data = load_data_from_db_visual(set_label="train")

    def generate_plotly_word_cloud_visuals(self):
        """ use plotly wordcloud to generate word cloud visuals """

        # social media messages word cloud
        social_media_messages = " ".join(
            self.data[self.data["genre"] == "social"]["message"]
        )
        social_media_messages = social_media_messages.translate(
            str.maketrans("", "", string.punctuation)
        )
        social_media_layout = plotly_wordcloud(
            social_media_messages, title="What People Are Saying On Social Media"
        )

        # news messages word cloud
        news_messages = " ".join(self.data[self.data["genre"] == "news"]["message"])
        news_messages = news_messages.translate(
            str.maketrans("", "", string.punctuation)
        )
        news_layout = plotly_wordcloud(
            news_messages, title="What People Are Saying In News"
        )

        # earthquake related messages
        direct_messages = " ".join(self.data[self.data["genre"] == "direct"]["message"])
        direct_messages = direct_messages.translate(
            str.maketrans("", "", string.punctuation)
        )
        direct_layout = plotly_wordcloud(
            direct_messages, title="What People Are Saying In Direct Messages"
        )

        # encode plotly graphs in JSON
        graphs = [news_layout, direct_layout, social_media_layout]
        return graphs
