import pandas as pd
from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, recall_score
from iapa.preML import split
import os

class Classification:
    def __init__(self, df, k, data_path):
        self.split_data = split(df)
        self.k = k
        self.data_path = data_path
        self.X_train = self.split_data[0]
        self.X_test = self.split_data[1]
        self.y_train = self.split_data[2]
        self.y_test = self.split_data[3]
        self.clf = svm.SVC(kernel = k)
    
    def execute(self): #Fit, predict and assess
        self.clf.fit(self.X_train, self.y_train.values.ravel())

        y_preds = self.clf.predict(self.X_test)

        results = {'Accuracy':0, 'Precision':0, 'Recall':0}
        results['Accuracy'] = round(accuracy_score(self.y_test, y_preds),5)
        results['Precision'] = round(precision_score(self.y_test, y_preds),5)
        results['Recall'] = round(recall_score(self.y_test, y_preds),5)
        
        pd.DataFrame(data=results, index=[0]).to_csv(os.path.join(self.data_path, "classification_metrics.csv"))
    
    
    def predict(self, X):
        preds = self.clf.predict(X)
        temp = pd.concat([X.reset_index(), pd.DataFrame(preds)], axis=1)
        temp.to_csv(os.path.join(self.data_path, "classification_predictions.csv"))
    