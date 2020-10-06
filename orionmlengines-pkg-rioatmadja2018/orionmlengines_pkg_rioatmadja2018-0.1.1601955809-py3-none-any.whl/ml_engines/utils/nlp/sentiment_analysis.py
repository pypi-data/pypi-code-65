#!/usr/bin/env python
import pandas as pd
import numpy as np
import re
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split, cross_val_score
from urllib import request
from scipy.sparse.csr import csr_matrix
from sklearn.metrics import jaccard_similarity_score

# Alias
from typing import Dict, List
from pandas.core.frame import DataFrame

# Exceptions
from pandas.errors import EmptyDataError
from urllib.error import HTTPError
np.random.seed(10000)


class SentimentAnalysis(object):
    """
    class SentimentAnalysis(object)
            SentimentAnalysis(text: str, ngrams: tuple, stop_words: str = 'english',  **kwargs)

    Function Description
    -----------
    This is an implementation of Sentiment Analysis class for DSC550 (Bellevue University) Week-4 Assignment. This class has the following methods:

    Private Functions
    -----------------
    - __load_corpus__: this function will download and parse the corpus from github
    - __load_classifier__: load the given classifier from the pickle file
    - __load_file__: this function will load the given pickle file
    - __save_classifiers__: save the classifier to local pickle file
    - __predict__: predict the given text based on the trained corpus

    Public Functions
    ----------------
    - to_csv: parse the string comma separated representation
    - predict_text: call the private function __predict__
    - fit: fit the corpus
    - get_labels: label the given text as positive or negative
    - get_accuracy: get the accuracy of the classifier
    - get_model_eval: get the score of the cross-validation from the given scoring method
    - to_csv: function to convert unstructured text into a comma separated form
    - get_roc_auc: calcluate the Receiver Operating Curve AUC

    Parameters
    ----------
    - texts: given a string of text
    - ngrams: optional parameters with default value (1,3)
    - stop_words: optional parameters with default value english
    - kwargs: for now clf and evaluate_model are supported (i.e. {clf: MultiNomialNB(), evaluate_model: True})
        - clf_name: given the classifier name
        - clf: given the Scikit-Learn Classifier Object
        - evaluate_model: If set to True, then it will compute the accuracy using cross validations
        - scoring: given the scoring methods
        - save_clf: pickle the classifiers

    Examples
    --------
    >>> sentiment_analysis = SentimentAnalysis(texts=["There' s nothing special happening today."], **{'clf': logreg} )
    >>> sentiment_analysis.fit()
    >>> sentiment_analysis.get_labels()
    >>> {'Text': ["There' s nothing special happening today."], 'Label': 'Positive'}
    """

    def __init__(self, texts: List, ngrams: tuple = (1, 3), stop_words: str = 'english', **kwargs):
        self.texts: str = texts
        self.ngrams: tuple = ngrams
        self.stop_words: str = stop_words
        self.parameters: Dict = kwargs

        # Local variable
        self.labels_: Dict = {}
        self.probability_: Dict = {}
        self.corpus: DataFrame = pd.DataFrame()
        self.corpus_link: str = "https://raw.githubusercontent.com/ratmadjads/DSC550/master/datasets/googleplaystore_user_reviews.csv"
        self.clf = None
        self.y_pred_class = None
        self.y_pred_proba = None
        self.y_true = None
        self.accuracy: float = 0.0
        self.roc_auc_score: float = 0.0
        self.clf_pickle_path: str = "./clf_df.pickle"
        self.model_eval: float = 0.0
        self.clf_name: str = self.parameters.get('clf_name', 'Logistic Regression')  # Default is Logistic Regression
        self.file_name: str = re.sub(' ', '_', self.clf_name)
        self.tfidf_transform_path: str = "tfidf_transform.pickle"
        self.word_vector_path: str = "word_vect.pickle"
        self.train_dataset_path: str = "training.pickle"
        self.test_dataset_path: str = "testing.pickle"
        self.train_dtm_path: str = "trained_dtm.pickle"  # path to the trained document-term matrix
        self.test_dtm_path: str = "test_dtm.pickle"

        if not self.texts and not isinstance(texts, List):
            raise ValueError(f"ERROR: you must provide parameter texts")

    def to_csv(self, text: str) -> object:
        """
        Descriptions
        -------------
        Helper function to parse string comma separated representation
        
        Parameters
        ----------
        :text: given a non empty comma separated representation text
        :return: an object such as list with comma separte attributes or np.nan if the review field is empty
        """

        if not isinstance(text, str):
            raise TypeError(f"ERROR: {text} must be str not type of {type(text)}")

        # replace with np.nan if there is no review from the corpus
        if not '\"' in text:
            return np.nan

        else:

            # Get the first and last index of double quotes
            first_index: int = text.index("\"")
            last_index: int = text.rindex("\"")

            if first_index and last_index:
                review = text[first_index:last_index]
                row = text.replace(review, "").split(',')
                row[1] = review  # append review
                return row[0:3] + list(filter(lambda column: re.match(r"[0-9]+\.[0-9]+", column), row))

            return np.nan

    def __load_corpus__(self) -> DataFrame:
        """
        Description
        -----------
        Helper function to download sample corpus from Github and remove the Null value by the sentiment column.
        
        Parameters
        ----------
        :return: a corpus dataframe
        """
        try:
            response = request.urlopen(
                request.Request(self.corpus_link, headers={'User-Agent': 'DSC550-Week4 Assignment',
                                                           'Accept': "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
                                                           }))
        except HTTPError as e:
            raise HTTPError(f"ERROR: Unable to download corpus from {self.corpus_link}") from e

        raw_data: List[str] = response.read().decode('utf-8').split('\r\n')
        corpus_df: DataFrame = pd.DataFrame(
            pd.DataFrame(raw_data[1:], columns=['Texts'])['Texts'].astype(str).apply(self.to_csv).dropna().tolist(),
            columns=raw_data[0].split(','))
        corpus_df = corpus_df.dropna(subset=['Sentiment'])
        corpus_df = corpus_df.query("Sentiment != 'Neutral'")  # Select positive and negative comments
        corpus_df['Translated_Review'] = corpus_df['Translated_Review'].astype(str)
        self.corpus = corpus_df

        return self.corpus

    def __load_classifier__(self) -> DataFrame:
        """
        Description
        -----------
        Helper function to load pickle file from local directory
        
        Parameters
        ----------
        :return: an empty dataframe with default column Classifier_Name and Classifier or dataframe that contains trained classifiers
        """
        if not os.path.exists(self.clf_pickle_path):
            return pd.DataFrame(columns=['Classifier_Name', 'Classifier'])  # return empty dataframe

        clf_df: DataFrame = pd.read_pickle(self.clf_pickle_path)
        return clf_df

    def __save_classifiers__(self) -> bool:
        """
        Description
        -----------
        Helper function to save classifiers to the local directory
        
        Parameters
        ----------
        :return: a boolean value, if it is successful then return True, otherwise False
        """
        clf_df: DataFrame = self.__load_classifier__()
        if clf_df['Classifier_Name'].str.count(
                self.clf_name).sum() == 0:  # append if the classifier does not exists in the pickle file
            clf_df = clf_df.append([{'Classifier_Name': self.clf_name, 'Classifier': self.clf}], ignore_index=True)
            clf_df.index = np.arange(1, clf_df.shape[0] + 1)

        clf_df.to_pickle(f"{self.clf_pickle_path}")
        return clf_df.shape[0] > 0 and os.path.exists(self.clf_pickle_path)

    def __save_obj__(self, *args):
        """
        Description
        ------------
        Helper function to save training and testing dataset, as well as the document-term matricies
        
        Parameters
        ----------
        :kwargs: given an optional argumens
        :return:
        """
        transform_tfidf, word_vect, training, testing, train_df, test_df = args

        pd.DataFrame({'TFIDF': transform_tfidf}, index=[1]).to_pickle(f"./{self.file_name}_{self.tfidf_transform_path}")
        pd.DataFrame({'Word_Vect': word_vect}, index=[1]).to_pickle(f"./{self.file_name}_{self.word_vector_path}")
        pd.DataFrame({'Train_DTM': training}, index=[1]).to_pickle(f"./{self.file_name}_{self.train_dtm_path}")
        pd.DataFrame({'Test_DTM': testing}, index=[1]).to_pickle(f"./{self.file_name}_{self.test_dtm_path}")
        train_df.to_pickle(f"./{self.file_name}_{self.train_dataset_path}")
        test_df.to_pickle(f"./{self.file_name}_{self.test_dataset_path}")

    def __load__file__(self, file_path: str, column_name: str = "") -> object:
        """
        Description
        -----------
        Generic function to load all pickle files and return accordingly
        
        Parameters
        ----------
        :file_path: given a valid file path
        :column_name: given column name to be pickle
        :return: an object
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ERROR: Unable to load file {file_path} because it is missing")

        return pd.read_pickle(file_path)[column_name].iloc[0] if column_name else pd.read_pickle(file_path)

    def predict_text(self, text: str):
        """
        Description
        -----------
        Helper function to be called by the client program
        
        Parameters
        ----------
        text: given non empty text
        :return: None
        """
        if not text:
            raise ValueError("Text cannot be emtpy.")

        self.__predict__(text=text)

    def __predict__(self, transform_tfidf: object = None, word_vect: object = None, text: str = ""):
        """
        Description
        -----------
        This function will predict the given text or comment as positive or negative based on the training corpus
        
        Parameters
        ----------
        :transform_tfidf: an optional parameter for transform_tfidf
        :word_vect: an optional parameter for word_vect
        :text: an optional parameter for non empty text
        :return: None
        """
        if not self.clf:
            raise ValueError(f"Must call the fit function before making prediction")

        if not transform_tfidf and not word_vect:
            transform_tfidf = self.__load__file__(file_path=f"./{self.file_name}_{self.tfidf_transform_path}",
                                                  column_name='TFIDF')
            word_vect = self.__load__file__(file_path=f"./{self.file_name}_{self.word_vector_path}",
                                            column_name='Word_Vect')

        negative, positive = tuple(
            self.clf.predict_proba(transform_tfidf.transform(word_vect.transform([text] if text else self.texts)))[0])
        self.labels_ = {'Text': text if text else self.texts,
                        'Label': 'Positive' if negative < positive and positive > 0.7 else 'Negative'}
        self.probability_ = {'Positive': positive,
                             'Negative': negative}

        return None

    def fit(self) -> bool:
        """
        Description
        -----------
        Classify the text based on the corpus, the default classifier is Logistic Regression unless it is provided by the kwargs
        Note: The corpus is trained on Google Play Store Reviews dataset
        Parameters
        ----------
        :return: a boolean True if it is successful otherwise return False
        """

        # Load the classifier and predict the given text or comment, if the classifier exists in the pickle file
        clf_df: DataFrame = self.__load_classifier__()
        if not clf_df.empty and clf_df['Classifier_Name'].str.count(self.clf_name).sum() > 0:
            self.clf = clf_df.query(f"Classifier_Name == '{self.clf_name}' ").iloc[0][-1]  # get specific classifier
            self.__predict__()
            return self.clf != None

        corpus: DataFrame = self.__load_corpus__()  # Load Google Play Store Reviews
        if corpus.empty:
            raise EmptyDataError("Something went wrong, corpus should not be empty. Please re-run again")

        response_vector = corpus.Sentiment.map(dict(
            zip(list(corpus.Sentiment.unique()), [1, 0])))  # Label Positive comments as 1 and Negative comments as 0
        corpus['response_vector'] = response_vector

        # Split to training and testing data
        train_df, test_df = train_test_split(corpus[['Translated_Review', 'response_vector']],
                                             random_state=np.random.randint(100, 200), test_size=0.2)

        # create a collection of a matrix of token counts and transform the count matrix to a normalized tf-idf representation
        word_vect = CountVectorizer(ngram_range=self.ngrams, stop_words=self.stop_words)
        word_counts = word_vect.fit_transform(train_df['Translated_Review'])
        transform_tfidf = TfidfTransformer()
        training = transform_tfidf.fit_transform(word_counts)
        word_counts_vector = word_vect.transform(test_df['Translated_Review'])
        testing = transform_tfidf.transform(word_counts_vector)

        # train Google Play Store Reviews
        self.clf = self.parameters.get('clf') if self.parameters.get('clf', None) else LogisticRegression(C=1e35)
        self.clf.fit(training, train_df['response_vector'])
        self.y_pred_class = self.clf.predict(testing)
        self.y_pred_proba = self.clf.predict_proba(testing)[:, 1]

        # If kwargs evaluate_model is provided use cross-validation instead
        if self.parameters.get('evaluate_model'):
            try:
                self.model_eval = cross_val_score(self.clf, training, train_df['response_vector'],
                                                  scoring=self.parameters.get('scoring') if self.parameters.get(
                                                      'scoring') else 'accuracy', cv=10).mean()
                return self.model_eval

            except ValueError as e:
                scoring_methods: List[str] = metrics.SCORERS.keys()
                raise ValueError(f"ERROR: Use the following scoring methods {scoring_methods}") from e

        self.__predict__(transform_tfidf=transform_tfidf, word_vect=word_vect)
        self.accuracy = metrics.accuracy_score(y_true=test_df['response_vector'], y_pred=self.y_pred_class)
        self.roc_auc_score = metrics.roc_auc_score(y_true=test_df['response_vector'], y_score=self.y_pred_proba)
        self.y_true = test_df['response_vector']

        # If kwargs save_clf is provided saved the trainined classifier into pickle file
        if self.parameters.get('save_clf'):
            # Save the initial classifier for quicker access
            if clf_df.empty:
                save_classifiers: bool = self.__save_classifiers__()
                if not save_classifiers:
                    raise ValueError(f"Unable to pickle the given {self.clf_name} classifier")

                # initially save word_vect and tfidf_tranform
                self.__save_obj__(*(transform_tfidf, word_vect, training, testing, train_df, test_df))

            # Load, Lookup, and append
            else:
                if self.clf_name == 'Logistic Regression':
                    raise ValueError(f"{self.clf_name} is the default classifier, please provide different classifier.")

                save_classifiers: bool = self.__save_classifiers__()
                self.__save_obj__(*(transform_tfidf, word_vect, training, testing, train_df, test_df))
                if not save_classifiers:
                    raise ValueError(f"Unable to pickle the given {self.clf_name} classifier")

        return self.clf != None  # if the self.clf has not been instantiated it will return false

    def get_labels(self) -> Dict:
        """
        Description
        -----------
        Helper function to return labeled text as positive or negative
        
        Parameters
        ----------
        :return: a dictionary with labeled text
        """
        if not self.labels_:
            raise ValueError("ERROR: Please call the fit function or re-run without evaluate_model = False.")

        return self.labels_

    def get_accuracy(self) -> float:
        """
        Description
        -----------
        Helper function to return the accuracy of the given classifier
        
        Parameters
        -----------
        :return: the accuracy score in float
        """
        if not self.accuracy:
            if os.path.exists(f"./{self.file_name}_{self.train_dataset_path}") and os.path.exists(
                    f"./{self.file_name}_{self.test_dataset_path}") and os.path.exists(
                    f"./{self.file_name}_{self.test_dtm_path}"):
                test_df: DataFrame = self.__load__file__(file_path=f"./{self.file_name}_{self.test_dataset_path}")
                testing: csr_matrix = \
                self.__load__file__(file_path=f"./{self.file_name}_{self.test_dtm_path}")['Test_DTM'].iloc[0]
                self.y_pred_class = self.clf.predict(testing)
                return metrics.accuracy_score(y_true=test_df['response_vector'], y_pred=self.y_pred_class)

            raise ValueError("ERROR: Please call the fit function or re-run without evaluate_model = False.")

        return self.accuracy

    def get_roc_auc(self) -> float:
        """
        Description
        -----------
        Helper function to calculate the area under the curve
        
        Parameters
        ----------
        :return: area under the curve score
        """
        if not self.roc_auc_score:
            if os.path.exists(f"./{self.file_name}_{self.train_dataset_path}") and os.path.exists(
                    f"./{self.file_name}_{self.test_dataset_path}") and os.path.exists(
                    f"./{self.file_name}_{self.test_dtm_path}"):
                test_df: DataFrame = self.__load__file__(file_path=f"./{self.file_name}_{self.test_dataset_path}")
                testing: csr_matrix = \
                self.__load__file__(file_path=f"./{self.file_name}_{self.test_dtm_path}")['Test_DTM'].iloc[0]
                self.y_true = test_df['response_vector']
                self.y_pred_proba = self.clf.predict_proba(testing)[:, 1]
                return metrics.roc_auc_score(y_true=test_df['response_vector'], y_score=self.y_pred_proba)

        return self.roc_auc_score

    def get_model_eval(self, scoring: str = "") -> float:
        """
        Description
        -----------
         Helper function to return the score based on the scoring method (e.g. accuracy, roc_auc)
        
         Parameters
        -----------
        :scoring: given a valid scoring methods
        :return: model evaluation score
        """
        if not self.model_eval:
            feature_matrix_path: str = f"{self.file_name}_{self.train_dtm_path}"
            response_vector_path: str = f"{self.file_name}_{self.train_dataset_path}"

            training: csr_matrix = self.__load__file__(file_path=feature_matrix_path)['Train_DTM'].iloc[0]
            train_df: DataFrame = self.__load__file__(file_path=response_vector_path)
            if os.path.exists(feature_matrix_path) and os.path.exists(response_vector_path):
                return cross_val_score(self.clf, training, train_df['response_vector'],
                                       scoring=self.parameters.get('scoring') if self.parameters.get(
                                           'scoring') else scoring, cv=10).mean()

            raise ValueError("ERROR: Please call the fit function or re-run without evaluate_model = False.")

        return self.model_eval
    def word_similarity(word_one: str,  word_two: str) -> float:
        """
        Description
        -----------
        Helper function to calculate the jaccard similarity between 2 words, by converting text-documents into a matrix of token counts
        
        Parameters
        ----------
        :word_one: given a non-emtpy string 
        :word_two: given a non-emtpy string
        :return: a jaccard score between two strings
        
        Examples
        --------
        >>> words: List[str] = ['IS is waging war in Lybia', 'ISIL is waging war in Iraq']
        >>> word_similarity('IS is waging war in Lybia', 'ISIL is waging war in Iraq')
        >>> 0.42857142857142855
        """
        if not word_one and word_two:
            raise ValueError("word_one and word_two are required parameters.")
        
        words: List[str] = [word_one.lower(), word_two.lower()]
        vect = CountVectorizer() 
        dtm = vect.fit_transform(words) 
        counts: DataFrame = pd.DataFrame( dtm.toarray() , columns=vect.get_feature_names())
        
        return jaccard_similarity_score(counts.iloc[0].tolist() , counts.iloc[-1].tolist())
