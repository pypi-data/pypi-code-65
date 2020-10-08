import spacy
import re
import html
import unicodedata
from cleantext import clean
import lxml.html.clean

class Cleaner():
    def __init__(self, language='nl', model_size='sm'):
        self.language = language
        self.model_size = model_size
        self.load_model()

    def load_model(self):
        model_name = self.language + "_core_news_" + self.model_size
        try:
            self.model = spacy.load(model_name)
        except:
            print("Spacy model error: {}".format(model_name))
        

    def clean(self, text, 
                    lower=False, 
                    clean_html=True,
                    clean_js=True,
                    fix_unicode=True,
                    to_ascii=False):
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Return normal form of the unicode string (e.g. remove \xa0 from string)
        if(fix_unicode):
            text = unicodedata.normalize('NFKD', text)
        
        # Remove JS code
        # First remove JS before removing other HTML tags.
        if(clean_js):
            js_cleaner = lxml.html.clean.Cleaner(comments=True, meta=True, scripts=True, embedded=True)
            text = js_cleaner.clean_html(text)

        # Remove HTML tags using a simple regex
        if(clean_html):
            text = re.sub('<.*?>', '', text)

        clean(text, fix_unicode=fix_unicode, to_ascii=to_ascii, lower=lower)

        return text