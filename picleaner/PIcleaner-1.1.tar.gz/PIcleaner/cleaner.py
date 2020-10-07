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
        

    def clean(self, text, lower=False, to_ascii=False, no_currency_symbols=False, fix_unicode=True, sentence_tokenize=False, clean_js = True, no_emails=False, no_phone_numbers=False, no_urls=False):
        self.load_model()
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Return normal form of the unicode string (e.g. remove \xa0 from string)
        if(fix_unicode):
            text = unicodedata.normalize('NFKD', text)
        
        clean(text,
              fix_unicode=fix_unicode,               # fix various unicode errors
              to_ascii=to_ascii,                  # transliterate to closest ASCII representation
              lower=lower,                     # lowercase text
              no_line_breaks=False,           # fully strip line breaks as opposed to only normalizing them
              no_urls=no_urls,                  # replace all URLs with a special token
              no_emails=no_emails,                # replace all email addresses with a special token
              no_phone_numbers=no_phone_numbers,         # replace all phone numbers with a special token
              no_numbers=False,               # replace all numbers with a special token
              no_digits=False,                # replace all digits with a special token
              no_currency_symbols=no_currency_symbols,      # replace all currency symbols with a special token
              no_punct=False,                 # fully remove punctuation
              replace_with_url="<URL>",
              replace_with_email="<EMAIL>",
              replace_with_phone_number="<PHONE>",
              replace_with_number="<NUMBER>",
              replace_with_digit="0",
              replace_with_currency_symbol="<CUR>",
             )
        
        # text = text.replace(' =','.')
        # text = text.replace('= ','.')
        # text = text.replace('=','.')
        # text = text.replace('&nbsp;','')
        # to_remove = "_.-()"
        # pattern = "(?P<char>[" + re.escape(to_remove) + "])(?P=char)+"

        # text = ' '.join(text.split())
        # # text = re.sub(r"[-()\"#/@;:<>{}=~|.?,]", "", text)
        # text = re.sub(pattern, r"\1", text)
        # text = re.sub(r"[\"#/@;:<>{}=~|?^$]", "", text)
        # text = text.replace(' .',' ')
        
        # Remove JS code
        # First remove JS before removing other HTML tags.
        if(clean_js):
            js_cleaner = lxml.html.clean.Cleaner(
                comments = True, # True = remove comments
                meta=True, # True = remove meta tags
                scripts=True, # True = remove script tags
                embedded = True, # True = remove embeded tags
            )
            text = js_cleaner.clean_html(text)

        # Remove HTML tags using a simple regex
        text = re.sub('<.*?>', '', text)

        # Sentence tokenization
        if(sentence_tokenize):
            doc = self.model(text)
            sentences = [token.text for token in doc.sents]

        return text, (sentences if sentence_tokenize else None) 