import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

class Polynomial():
    def __init__(self):
        super().__init__()
    def initModel(self):
        self.model = LinearRegression(fit_intercept=False)
    def fit(self, x, y):
        self.model.fit(x, y)
    def predict(self, val):
        return self.model.predict(val)    
    def score(self, x, y):
        r_sq = self.model.score(x, y)
        return r_sq
    def coef(self):
        return self.model.coef_
    def intercept(self):
        return self.model.intercept_                