import langid
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words

from pdf_extractor.cleaning_encoding import clean_encoding


def summarize_text(text, n_sentences, force=False):
    """Summarizing a text

    Args:
        text (str): Text to summarize
        n_sentences (int): Number of sentences that should be used to summarize
        the text
        force (bool, optional): Whether to force the summarization for non-english
        texts. Defaults to False.

    Raises:
        UnsupportedLanguage: If not forcing the summarization and the detected
        language is not english, then this is raised

    Returns:
        str: Summary of the text passed as input
    """

    LANG = "english"
    # Checking the language of the text to summarize
    language = langid.classify(text)[0]

    if (language != "en") & (force == False):
        message = 'At the moment, only english language is supported but we ' \
                    f'detected a text in "{language}", please pass "force" ' \
                    'argument to True if you want to force the summarization of the text '
        raise UnsupportedLanguage(message)
    
    parser = PlaintextParser.from_string(text, Tokenizer(LANG))
    stemmer = Stemmer(LANG)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANG)
    sentences = [str(x) for x in summarizer(parser.document, n_sentences)]
    sentences = " ".join(sentences)
    sentences = clean_encoding().clean(sentences)

    return sentences

class UnsupportedLanguage():
    def __init__(self, message):
        self.message = message
