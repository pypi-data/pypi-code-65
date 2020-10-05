"""
A text tokenizer class , fully written from scratch.
"""


import re
import string
from .stopwords import STOP_WORDS


# stop_words = list(map(lambda s: s.strip(), stop_words))
stop_words = STOP_WORDS



class NepaliTokenizer:
    
    def __init__(self ,punct=[]):
        """
        #Parameter:

        punct-> Punctuation (Input your own punctuation)

        """

        self.user_defined_punctuation = punct
        self.punctuation = ["\ufeff" , '\n' , '<br>' , '॥','।'] + list(string.punctuation)

        if self.user_defined_punctuation:
            self.punctuation += self.user_defined_punctuation
    
    def tokenizer(self , text):
        """
        Input text corpus to tokenize.

        #Parameter:
        
        ---- text(str)-> returns list.

        """


        for punct in self.punctuation:
            text = ' '.join(text.split(punct))

        text = re.sub('\d+' , ' ',text)

        text = text.split(' ')
        nepali_tokens = []

        for t in text:
            if t not in stop_words:
                if t != '' and t not in self.punctuation:
                    nepali_tokens.append(t)

        return nepali_tokens

    
    def __str__(self):
        return 'Input extra punctuation for tokenizing a corpus.'
        

