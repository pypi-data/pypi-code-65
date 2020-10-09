import html

import bbcode
import ftfy


class clean_encoding():
    """Class that allows the cleaning of text
    """

    def __init__(self):
        self.parser = bbcode.Parser()

    def fix_text(self, text):
        """Fix bad characters' encoding

        Args:
            text (str): text to clean

        Returns:
            str: cleaned text
        """

        text = ftfy.fix_encoding(text)
        return text

    def replacement(self, text):
        """Unescape every html entity

        Args:
            text (str): text fo clean

        Returns:
            str: unescaped text
        """

        return html.unescape(text)

    def bbcode(self, text):
        """Remove every bbcode tags

        Args:
            text (str): text to clean

        Returns:
            str: text with stripped bbcode tags
        """

        plain_txt = self.parser.strip(text)
        return plain_txt

    def clean(self, text):
        """Clean a piece of text using by stripping bbcode tags, unescaping
        html entities and fixing badly encoded characters

        Args:
            text (str): text to clean

        Returns:
            str: cleaned text
        """
        
        text = self.fix_text(text)
        text = self.replacement(text)
        text = self.bbcode(text)
        text = ' '.join(text.split())
        text = text.strip()

        return text


