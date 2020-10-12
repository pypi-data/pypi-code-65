import numpy
from matchms import Scores, Spectrum
from matchms.similarity import CosineGreedy, IntersectMz
from matchms.similarity.BaseSimilarity import BaseSimilarity




#%%
import numpy
from matchms import Scores, Spectrum
from matchms.similarity import CosineGreedy

"Test scores_by_reference method."
spectrum_1 = Spectrum(mz=numpy.array([100, 150, 200.]),
                      intensities=numpy.array([0.7, 0.2, 0.1]),
                      metadata={'id': 'spectrum1'})
spectrum_2 = Spectrum(mz=numpy.array([100, 140, 190.]),
                      intensities=numpy.array([0.4, 0.2, 0.1]),
                      metadata={'id': 'spectrum2'})
spectrum_3 = Spectrum(mz=numpy.array([110, 140, 195.]),
                      intensities=numpy.array([0.6, 0.2, 0.1]),
                      metadata={'id': 'spectrum3'})
spectrum_4 = Spectrum(mz=numpy.array([100, 150, 200.]),
                      intensities=numpy.array([0.6, 0.1, 0.6]),
                      metadata={'id': 'spectrum4'})
references = [spectrum_1, spectrum_2, spectrum_3]
queries = [spectrum_3, spectrum_4]

scores = Scores(references, queries, CosineGreedy()).calculate()
selected_scores = scores.scores_by_reference(spectrum_2)

expected_result = [(scores.queries[:, i][0], *scores.scores[1, i]) for i in range(2)]
assert selected_scores == expected_result, "Expected different scores."


# def test_scores_by_query():
"Test scores_by_query method."
spectrum_1 = Spectrum(mz=numpy.array([100, 150, 200.]),
                      intensities=numpy.array([0.7, 0.2, 0.1]),
                      metadata={'id': 'spectrum1'})
spectrum_2 = Spectrum(mz=numpy.array([100, 140, 190.]),
                      intensities=numpy.array([0.4, 0.2, 0.1]),
                      metadata={'id': 'spectrum2'})
spectrum_3 = Spectrum(mz=numpy.array([110, 140, 195.]),
                      intensities=numpy.array([0.6, 0.2, 0.1]),
                      metadata={'id': 'spectrum3'})
spectrum_4 = Spectrum(mz=numpy.array([100, 150, 200.]),
                      intensities=numpy.array([0.6, 0.1, 0.6]),
                      metadata={'id': 'spectrum4'})
references = [spectrum_1, spectrum_2, spectrum_3]
queries = [spectrum_2, spectrum_3, spectrum_4]

scores = Scores(references, queries, CosineGreedy()).calculate()
selected_scores = scores.scores_by_query(spectrum_4)

expected_result = [(scores.references[i][0], *scores.scores[i, 2]) for i in range(3)]
assert selected_scores == expected_result, "Expected different scores."


#%%
import numpy as np
from matchms import Scores, Spectrum
from matchms.similarity import CosineGreedy

spectrum_1 = Spectrum(mz=np.array([100, 150, 200.]),
                      intensities=np.array([0.7, 0.2, 0.1]),
                      metadata={'id': 'spectrum1'})
spectrum_2 = Spectrum(mz=np.array([100, 140, 190.]),
                      intensities=np.array([0.4, 0.2, 0.1]),
                      metadata={'id': 'spectrum2'})
spectrum_3 = Spectrum(mz=np.array([110, 140, 195.]),
                      intensities=np.array([0.6, 0.2, 0.1]),
                      metadata={'id': 'spectrum3'})
spectrum_4 = Spectrum(mz=np.array([100, 150, 200.]),
                      intensities=np.array([0.6, 0.1, 0.6]),
                      metadata={'id': 'spectrum4'})
references = [spectrum_1, spectrum_2, spectrum_3]
queries = [spectrum_2, spectrum_3, spectrum_4]

scores = Scores(references, queries, CosineGreedy()).calculate()
selected_scores = scores.scores_by_query(spectrum_4)
selected_scores.sort(key=lambda s: s[1], reverse=True)
print([x[1].round(3) for x in selected_scores])


#%%
spectrums = []
for i in range(50000):
    mzs=np.array([100, 150, 200.]) + np.random.uniform(0, 10, 3)
    spectrums.append(Spectrum(mz=np.array([100, 150, 200.]),
                              intensities=np.array([0.7, 0.2, 0.1]),
                              metadata={'id': 'spectrum'+str(i)}))

scores = Scores(spectrums, queries, CosineGreedy()).calculate()
#%%
import timeit

scores = Scores(spectrums, queries, CosineGreedy()).calculate()

selected_scores = scores.scores_by_query(spectrum_4)
%timeit selected_scores = scores.scores_by_query(spectrum_4)

#%%
#%%
import timeit
selected_scores = scores.scores_by_query(spectrum_4)
%timeit selected_scores = scores.scores_by_query(spectrum_4)

