import os
import gensim
import pytest
from matchms import calculate_scores_parallel
from matchms.filtering import add_losses
from matchms.filtering import add_parent_mass
from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities
from matchms.filtering import require_minimum_number_of_peaks
from matchms.filtering import select_by_mz
from matchms.filtering import reduce_to_number_of_peaks
from matchms.importing import load_from_mgf
from spec2vec import Spec2VecParallel
from spec2vec import SpectrumDocument


# def test_user_workflow_spec2vec_parallel():

def apply_my_filters(s):
    s = default_filters(s)
    s = add_parent_mass(s)
    s = normalize_intensities(s)
    s = reduce_to_number_of_peaks(s, n_required=10, ratio_desired=0.5)
    s = select_by_mz(s, mz_from=0, mz_to=1000)
    s = add_losses(s, loss_mz_from=10.0, loss_mz_to=200.0)
    s = require_minimum_number_of_peaks(s, n_required=5)
    return s

repository_root = os.path.join(os.path.dirname(__file__), "..")
spectrums_file = os.path.join(repository_root, "tests", "pesticides.mgf")

# apply my filters to the data
spectrums = [apply_my_filters(s) for s in load_from_mgf(spectrums_file)]

# omit spectrums that didn't qualify for analysis
spectrums = [s for s in spectrums if s is not None]

documents = [SpectrumDocument(s) for s in spectrums]

model_file = os.path.join(repository_root, "integration-tests", "test_user_workflow_spec2vec.model")
if os.path.isfile(model_file):
    model = gensim.models.Word2Vec.load(model_file)
else:
    # create and train model
    model = gensim.models.Word2Vec([d.words for d in documents], size=10, min_count=1)
    model.train([d.words for d in documents], total_examples=len(documents), epochs=20)
    model.save(model_file)

# define similarity_function
spec2vec = Spec2VecParallel(model=model, intensity_weighting_power=0.5)

references = documents[:26]
queries = documents[25:]

# calculate scores on all combinations of references and queries
scores = list(calculate_scores_parallel(references, queries, spec2vec))

# filter out self-comparisons
filtered = [(reference, query, score) for (reference, query, score) in scores if reference != query]

sorted_by_score = sorted(filtered, key=lambda elem: elem[2], reverse=True)

actual_top10 = sorted_by_score[:10]

expected_top10 = [
    (documents[19], documents[25], pytest.approx(0.9999121928249473, rel=1e-9)),
    (documents[20], documents[25], pytest.approx(0.9998846890269892, rel=1e-9)),
    (documents[20], documents[45], pytest.approx(0.9998756073673759, rel=1e-9)),
    (documents[25], documents[45], pytest.approx(0.9998750427994474, rel=1e-9)),
    (documents[19], documents[27], pytest.approx(0.9998722768460854, rel=1e-9)),
    (documents[22], documents[27], pytest.approx(0.9998633023352553, rel=1e-9)),
    (documents[18], documents[27], pytest.approx(0.9998616961532616, rel=1e-9)),
    (documents[19], documents[45], pytest.approx(0.9998528723697396, rel=1e-9)),
    (documents[14], documents[71], pytest.approx(0.9998404364805897, rel=1e-9)),
    (documents[20], documents[27], pytest.approx(0.9998336807761137, rel=1e-9))
]

assert actual_top10 == expected_top10, "Expected different top 10 table."


#%%
import os
import gensim
import pytest
from matchms import calculate_scores
from matchms.filtering import add_losses
from matchms.filtering import add_parent_mass
from matchms.filtering import default_filters
from matchms.filtering import normalize_intensities
from matchms.filtering import reduce_to_number_of_peaks
from matchms.filtering import require_minimum_number_of_peaks
from matchms.filtering import select_by_mz
from matchms.importing import load_from_mgf
from spec2vec import Spec2Vec
from spec2vec import SpectrumDocument


# def test_user_workflow_spec2vec():
"""Test typical user workflow to get from mass spectra to spec2vec similarities.

This test will run a typical workflow example using a small dataset and a
pretrained word2vec model. One main aspect of this is to test if users will
get exactly the same spec2vec similarity scores when starting from a word2vec
model that was trained and saved elsewhere.
"""
def apply_my_filters(s):
    """This is how a user would typically design his own pre- and post-
    processing pipeline."""
    s = default_filters(s)
    s = add_parent_mass(s)
    s = normalize_intensities(s)
    s = reduce_to_number_of_peaks(s, n_required=10, ratio_desired=0.5)
    s = select_by_mz(s, mz_from=0, mz_to=1000)
    s = add_losses(s, loss_mz_from=10.0, loss_mz_to=200.0)
    s = require_minimum_number_of_peaks(s, n_required=5)
    return s

repository_root = os.path.join(os.path.dirname(__file__), "..")
spectrums_file = os.path.join(repository_root, "tests", "pesticides.mgf")

# apply my filters to the data
spectrums = [apply_my_filters(s) for s in load_from_mgf(spectrums_file)]

# omit spectrums that didn't qualify for analysis
spectrums = [s for s in spectrums if s is not None]

documents = [SpectrumDocument(s) for s in spectrums]

model_file = os.path.join(repository_root, "integration-tests", "test_user_workflow_spec2vec.model")
if os.path.isfile(model_file):
    model = gensim.models.Word2Vec.load(model_file)
else:
    # create and train model
    model = gensim.models.Word2Vec([d.words for d in documents], size=5, min_count=1)
    model.train([d.words for d in documents], total_examples=len(documents), epochs=20)
    model.save(model_file)

# define similarity_function
spec2vec = Spec2Vec(model=model, intensity_weighting_power=0.5)

references = documents[:26]
queries = documents[25:]

# calculate scores on all combinations of references and queries
scores = list(calculate_scores(references, queries, spec2vec))

# filter out self-comparisons
filtered = [(reference, query, score) for (reference, query, score) in scores if reference != query]

sorted_by_score = sorted(filtered, key=lambda elem: elem[2], reverse=True)

actual_top10 = sorted_by_score[:10]

expected_top10 = [
    (documents[19], documents[25], pytest.approx(0.9999121928249473, rel=1e-9)),
    (documents[20], documents[25], pytest.approx(0.9998846890269892, rel=1e-9)),
    (documents[20], documents[45], pytest.approx(0.9998756073673759, rel=1e-9)),
    (documents[25], documents[45], pytest.approx(0.9998750427994474, rel=1e-9)),
    (documents[19], documents[27], pytest.approx(0.9998722768460854, rel=1e-9)),
    (documents[22], documents[27], pytest.approx(0.9998633023352553, rel=1e-9)),
    (documents[18], documents[27], pytest.approx(0.9998616961532616, rel=1e-9)),
    (documents[19], documents[45], pytest.approx(0.9998528723697396, rel=1e-9)),
    (documents[14], documents[71], pytest.approx(0.9998404364805897, rel=1e-9)),
    (documents[20], documents[27], pytest.approx(0.9998336807761137, rel=1e-9))
]

assert actual_top10 == expected_top10, "Expected different top 10 table."



#%%
import os
import gensim
import numpy
import pytest
from matchms import Spectrum
from spec2vec import SpectrumDocument
from spec2vec.calc_vector import calc_vector


# def test_calc_vector():
"""Test deriving a document vector using a pretrained network."""
spectrum = Spectrum(mz=numpy.array([100, 150, 200, 250], dtype="float"),
                    intensities=numpy.array([0.1, 0.1, 0.1, 1.0], dtype="float"),
                    metadata={})

document = SpectrumDocument(spectrum, n_decimals=1)
model = import_pretrained_model()
vector = calc_vector(model, document, intensity_weighting_power=0.5, allowed_missing_percentage=1.0)
expected_vector = numpy.array([ 0.08982063, -1.43037023, -0.17572929, -0.45750666, 0.44942236,
                               1.35530729, -1.8305029 , -0.36850534, -0.28393048, -0.34192028])
assert numpy.all(vector == pytest.approx(expected_vector, 1e-5)), "Expected different document vector."


# def test_calc_vector_higher_than_allowed_missing_percentage():
"""Test using a pretrained network and a missing word percentage above allowed."""
spectrum = Spectrum(mz=numpy.array([11.1, 100, 200, 250], dtype="float"),
                    intensities=numpy.array([0.1, 0.1, 0.1, 1.0], dtype="float"),
                    metadata={})

document = SpectrumDocument(spectrum, n_decimals=1)
model = import_pretrained_model()
assert document.words[0] not in model.wv.vocab, "Expected word to be missing from given model."
with pytest.raises(AssertionError) as msg:
    calc_vector(model, document, intensity_weighting_power=0.5, allowed_missing_percentage=16.0)

expected_message_part = "Missing percentage is larger than set maximum."
assert expected_message_part in str(msg.value), "Expected particular error message."


# def test_calc_vector_within_allowed_missing_percentage():
"""Test using a pretrained network and a missing word percentage within allowed."""
spectrum = Spectrum(mz=numpy.array([11.1, 100, 200, 250], dtype="float"),
                    intensities=numpy.array([0.1, 0.1, 0.1, 1.0], dtype="float"),
                    metadata={})

document = SpectrumDocument(spectrum, n_decimals=1)
model = import_pretrained_model()
vector = calc_vector(model, document, intensity_weighting_power=0.5, allowed_missing_percentage=17.0)
expected_vector = numpy.array([ 0.12775915, -1.17673617, -0.14598507, -0.40189132, 0.36908966,
                               1.11608575, -1.46774333, -0.31442554, -0.23168877, -0.29420064])
assert document.words[0] not in model.wv.vocab, "Expected word to be missing from given model."
assert numpy.all(vector == pytest.approx(expected_vector, 1e-5)), "Expected different document vector."

#%%
def import_pretrained_model():
    repository_root = os.path.join(os.path.dirname(__file__), "..")
    model_file = os.path.join(repository_root, "integration-tests", "test_user_workflow_spec2vec.model")
    return gensim.models.Word2Vec.load(model_file)

