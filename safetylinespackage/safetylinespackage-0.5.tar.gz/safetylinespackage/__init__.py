
import json
import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.metrics import confusion_matrix

from safetylinespackage.safetylinespackage import generate,get_metric,learn,learn,predict,target_statistics,features_statistics,correlation,statistics,print_correlations
