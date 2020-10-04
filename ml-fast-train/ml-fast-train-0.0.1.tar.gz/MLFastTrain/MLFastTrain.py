from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier, RandomForestRegressor, AdaBoostRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, ExtraTreeClassifier, ExtraTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.svm import SVC, SVR

from sklearn.model_selection import train_test_split
from tqdm import tqdm
from time import time
from prettytable import PrettyTable
import sys

class MLFastTrainer:
    def __init__(self, problem_type, splits=0):
        self.problem_type = problem_type
        self.splits = splits
        self.stats = {}
        if problem_type == 'classification':
            self.algorithms = [
                RandomForestClassifier(),
                AdaBoostClassifier(), 
                ExtraTreesClassifier(), 
                ExtraTreeClassifier(),
                KNeighborsClassifier(), 
                LogisticRegression(),
                XGBClassifier(),
                LGBMClassifier(),
                SVC()
            ]
        if problem_type == 'regression':
            self.algorithms = [
                RandomForestRegressor(),
                AdaBoostRegressor(), 
                ExtraTreesRegressor(),
                ExtraTreeRegressor(), 
                KNeighborsRegressor(), 
                LogisticRegression(),
                LinearRegression(),
                XGBRegressor(objective='reg:squarederror'),
                LGBMRegressor(),
                SVR()
            ]
            
    def __base_fit(self, model, X_train, X_test, y_train, y_test):
        t0 = time()
        instance = model.fit(X_train, y_train)
        self.stats[model.__class__.__name__] = {}
        self.stats[model.__class__.__name__]['training_time'] = round(time() - t0, 4)
        self.stats[model.__class__.__name__]['params'] = instance.get_params()
        self.stats[model.__class__.__name__]['train_score'] = round(model.score(X_train, y_train), 2)
        self.stats[model.__class__.__name__]['test_score'] = round(model.score(X_test, y_test), 2)
        
        
    def __print(self, msg, chariot=False):
        if chariot:
            msg = '\r' + msg
        sys.stdout.write(msg)
        sys.stdout.flush()
        
    def add_custome_model(self, model):
        try:
            model.__class__.__name__
            self.algorithms.append(model)
        except Exception as e:
            print(e)
        
    def fit(self, X, y):
        if self.splits < 2 or self.splits == None:
            X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        for model in self.algorithms:
            try:
                self.__print("\n{:<30} [{}]".format(model.__class__.__name__, "fitting"))
                self.__base_fit(model, X_train, X_test, y_train, y_test)
                self.__print("{:<30} [{}]".format(model.__class__.__name__, "Finished"), chariot=True)
            except Exception as e:
                self.__print("{:<30} [{}]".format(model.__class__.__name__, "ERROR " + str(e)), chariot=True)
        return self
    
    def getStats(self):
        return self.stats
        
    def printStats(self, sort_by='test_score'):
        sorted_stats = {
            k: v for k, v in 
            sorted(self.stats.items(), key=lambda item: item[1][sort_by], reverse=True)
        }
        best_train_score = max([sorted_stats[model]['train_score'] for model in sorted_stats])
        best_test_score = max([sorted_stats[model]['test_score'] for model in sorted_stats])
        best_training_time = min([sorted_stats[model]['training_time'] for model in sorted_stats])
        
        pt = PrettyTable()
        pt.field_names = ["Model", "Train time", "Train score", "Test score"]
        for model_name in sorted_stats:
            pt.add_row([
                model_name, 
                str(self.stats[model_name]['training_time']) + "*" if self.stats[model_name]['training_time'] <= best_training_time else self.stats[model_name]['training_time'],
                str(self.stats[model_name]['train_score']) + "*" if self.stats[model_name]['train_score'] >= best_train_score else self.stats[model_name]['train_score'],
                str(self.stats[model_name]['test_score']) + "*" if self.stats[model_name]['test_score'] >= best_test_score else self.stats[model_name]['test_score']
            ])

        print(pt)
        print("(* is Best)")