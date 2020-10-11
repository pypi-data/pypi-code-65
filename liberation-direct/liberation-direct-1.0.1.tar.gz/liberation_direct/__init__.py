import requests

from bs4 import BeautifulSoup
from markdownify import markdownify

""" URL of the Libération Live. """
LIVE_URL = "https://www.liberation.fr/direct/"

""" Keywords that are usually present in the news summary articles. """
NEWS_SUMMARY_KEYWORDS = [
    "actu à midi",
    "actu du week-end",
    "actualité de ce",
    "actu de ce",
    "à la mi-journée",
    "le point sur l'actu",
]


class LiveElement:
    """ One element in Libération's live.

    Args:
        html_content (bs4.element.Tag)

    """

    def __init__(self, html_content):
        self.html_content = html_content

    @property
    def title_html(self):
        """ Returns the element's title tag."""
        html_element = self.html_content.find_all("h3", class_="live-title")
        return html_element or None

    @property
    def title_text(self):
        """ Returns the element's title text. """
        if not self.title_html:
            return None

        return self.title_html[0].find("a").text

    @property
    def is_summary(self):
        """ Checks whether this element is a news summary. """
        return any(s in self.title_text for s in NEWS_SUMMARY_KEYWORDS)

    def to_markdown(self):
        """ Converts the element to a Markdown string. """
        md = [markdownify(self.title_html[0].decode())]
        for c in self.html_content.find("span").contents:
            md.append(markdownify(c.decode()))

        return "".join(md)


class LiberationDirect:
    """ API to parse Libération's news live into markdown. """

    def parse_live(self):
        """ Reads the contents of the live url. """
        live_page_contents = requests.get(LIVE_URL).content
        live_page_data = BeautifulSoup(live_page_contents, "html.parser")
        articles = live_page_data.find_all("div", class_="live-content")
        return [LiveElement(html_content=art) for art in articles]

    def get_news_summary_markdown(self):
        """ Finds the latest news summary and converts it into markdown. """
        for element in self.parse_live():
            if element.is_summary:
                return element.to_markdown()

        return None
