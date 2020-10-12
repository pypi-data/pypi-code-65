import numpy
import pytest
from matchms import Scores


class DummySimilarityFunction:
    def __init__(self):
        """constructor"""

    def __call__(self, reference, query):
        """call method"""
        s = reference + query
        return s, len(s)


class DummySimilarityFunctionParallel:
    def __init__(self):
        """constructor"""

    def __call__(self, references, queries):
        """call method"""
        shape = len(references), len(queries)
        s = numpy.empty(shape, dtype="object")
        for index_reference, reference in enumerate(references):
            for index_query, query in enumerate(queries):
                rq = reference + query
                s[index_reference, index_query] = rq, len(rq)
        return s


# def test_scores_calculate():
dummy_similarity_function = DummySimilarityFunction()
scores = Scores(references=["r0", "r1", "r2"],
                queries=["q0", "q1"],
                similarity_function=dummy_similarity_function)
scores.calculate()
actual = list(scores)
expected = [
    ("r0", "q0", "r0q0", 4),
    ("r0", "q1", "r0q1", 4),
    ("r1", "q0", "r1q0", 4),
    ("r1", "q1", "r1q1", 4),
    ("r2", "q0", "r2q0", 4),
    ("r2", "q1", "r2q1", 4)
]
assert actual == expected

#%%
import numpy as np
from matchms import calculate_scores, Spectrum
from matchms.similarity import ParentmassMatch, ParentmassMatchParallel

spectrum_1 = Spectrum(mz=np.array([100, 150, 200.]),
                      intensities=np.array([0.7, 0.2, 0.1]),
                      metadata={'parent_mass': 100})
spectrum_2 = Spectrum(mz=np.array([100, 140, 190.]),
                      intensities=np.array([0.4, 0.2, 0.1]),
                      metadata={'parent_mass': 100.01})
spectrum_3 = Spectrum(mz=np.array([90, 130, 191.]),
                      intensities=np.array([0.54, 0.22, 0.41]),
                      metadata={'parent_mass': 110})
spectrums = [spectrum_1, spectrum_2, spectrum_3]
references = spectrums
queries = spectrums

scores1 = Scores(references, queries, ParentmassMatch()).calculate().scores  # correct one if you want sequential
scores2 = Scores(references, queries, ParentmassMatchParallel()).calculate_parallel().scores  # correct one if you want parallel
scores3 = Scores(references, queries, ParentmassMatchParallel()).calculate().scores  # will fail
scores4 = Scores(references, queries, ParentmassMatch()).calculate_parallel().scores  # will fail

#%%
import inspect

class DummySimilarityFunctionNew:
    def __init__(self):
        """constructor"""

    def __call__(self, reference, query, is_parallel=False):
        """call method"""
        if is_parallel:
            return self.compute_scores_parallel(reference, query)
        return self.compute_scores(reference, query)

    def compute_scores(self, reference, query):
        """basic method, always provided for similarity scores"""
        s = reference + query
        return s, len(s)

    def compute_scores_parallel(self, reference, query):
        """parallel method, only provided for some similarity scores"""
        shape = len(references), len(queries)
        s = numpy.empty(shape, dtype="object")
        for index_reference, reference in enumerate(references):
            for index_query, query in enumerate(queries):
                rq = reference + query
                s[index_reference, index_query] = rq, len(rq)
        return s
  
dummy_similarity_function = DummySimilarityFunctionNew()
scores = Scores(references=["r0", "r1", "r2"],
                queries=["q0", "q1"],
                similarity_function=dummy_similarity_function)
scores.calculate()
actual = list(scores)    

#%%
@staticmethod
def _validate_input_arguments(references, queries, similarity_function, is_symmetric):
    assert isinstance(references, (list, tuple, numpy.ndarray)),\
        "Expected input argument 'references' to be list or tuple or numpy.ndarray."

    assert isinstance(queries, (list, tuple, numpy.ndarray)),\
        "Expected input argument 'queries' to be list or tuple or numpy.ndarray."

    assert callable(similarity_function), "Expected input argument 'similarity_function' to be callable."

    if is_symmetric:
        assert len(references) == len(queries), "Expect references and queries to be the same."

    def _chose_parallel_implementation(self):
        """
        Chose implementation for calculating the scores based on input dimensions and
        available score implementations (e.g. parallel or only sequential).
        """    
        # Check if parallel implementation exists
        similarity_methods = dict((name, func) for name, func in inspect.getmembers(self.similarity_function))
        if "compute_scores_parallel" not in similarity_methods:
            return False

        # Check if input is likely to benefit from parallel implementation 
        if len(references) > 1 and len(queries) > 1:
            return True
        return False
        
    
    def calculate(self) -> Scores:
        """
        Calculate the similarity between all reference objects v all query objects using
        the most suitable available implementation of the given similarity_function.
        """
        if self._chose_parallel_implementation():
            return self.calculate_parallel()
        return self.calculate_sequential()
    
    def calculate_sequential(self) -> Scores:
        """
        Calculate the similarity between all reference objects v all query objects using a
        naive implementation (i.e. a double for-loop). Similarity functions should expect
        one reference and one query object as its input arguments.
        """
        for i_ref, reference in enumerate(self.references[:self.n_rows, 0]):
            if self.is_symmetric:
                for i_query, query in enumerate(self.queries[0, i_ref:self.n_cols], start=i_ref):
                    self._scores[i_ref][i_query] = self.similarity_function(reference, query)
                    self._scores[i_query][i_ref] = self._scores[i_ref][i_query]
            else:
                for i_query, query in enumerate(self.queries[0, :self.n_cols]):
                    self._scores[i_ref][i_query] = self.similarity_function(reference, query)
        return self
    
    def calculate_parallel(self) -> Scores:
        """
        Calculate the similarity between all reference objects v all query objects using a
        vectorized implementation.  Similarity functions should expect a Numpy array of
        all reference objects and a Numpy array of all query objects as its input arguments.
        """
        signature = inspect.signature(self.similarity_function)
        if "is_symmetric" in str(signature):
            self._scores = self.similarity_function(self.references[:, 0], self.queries[0, :],
                                                    is_parallel=True, is_symmetric=self.is_symmetric)
        else:
            self._scores = self.similarity_function(self.references[:, 0], self.queries[0, :],
                                                    is_parallel=True)
        return self



