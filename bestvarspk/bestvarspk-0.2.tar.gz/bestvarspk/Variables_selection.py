import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.svm import SVR
from .General_variables import Best_variables


class Selection(Best_variables):
    """ Selection variable class for computing and 
    visualizing the best features intended.
 
    Attributes:
        df (dataframe) representing the data in pandas format
        target (string) representing target column
        rgr (boolean) representing target column as Regression(True) or Classification(False)
    """

    def __init__(self, df, target, rgr=False):

        Best_variables.__init__(self, df, target, rgr)

    def kbest_features(self, num):

        """Function to calculate the bests features with selectKBest.

            Args: 
            num (int) representing the number min number of features.

            Returns: 
                print of best features

        """
        # apply SelectKBest class to extract top 10 best features
        bestfeatures = SelectKBest(score_func=chi2, k=num)
        X = self.x
        y = self.y
        fit = bestfeatures.fit(X, y)
        dfscores = pd.DataFrame(fit.scores_)
        dfcolumns = pd.DataFrame(X.columns)

        # concat two dataframes for better visualization
        featureScores = pd.concat([dfcolumns, dfscores], axis=1)
        featureScores.columns = ["Specs", "Score"]  # naming the dataframe columns
        print(featureScores.nlargest(num, "Score"))  # print 10 best features

    def importance_features(self, num, typ):

        """Function to calculate the bests features with feature importance with ExtraTreesClassifier or 
        RandomForestClassifier.

            Args: 
            num (int) representing the number min number of features.
            typ (string) representing the type of model RandomForestClassifier (rfc) or ExtraTreesClassifier (etc).
            Returns: 
                plot best features.

        """
        X = self.x
        y = self.y

        if typ is "etc":
            model = ExtraTreesClassifier()
            model.fit(X, y)
            # print(model.feature_importances_)

            # plot graph of feature importances for better visualization
            feat_importances = pd.Series(model.feature_importances_, index=X.columns)
            feat_importances.nlargest(num).plot(kind="barh")
            plt.show()

        elif typ is "rfc":
            X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
            model = RandomForestClassifier()
            model.fit(X_train, y_train)

            # plot graph of feature importances for better visualization
            importances = pd.Series(data=model.feature_importances_, index=X.columns)
            sns.barplot(x=importances, y=importances.index, orient="h").set_title(
                "Importância de cada feature"
            )

    def corr_features(self):

        """Function to calculate the correlation of features.

            Args: 
                None.

            Returns: 
                plot best correlation.

        """
        data = self.df
        corrmat = data.corr()
        top_corr_features = corrmat.index
        plt.figure(figsize=(20, 20))

        # plot heat map
        g = sns.heatmap(data[top_corr_features].corr(), annot=True, cmap="Blues")

    def rfe_features(self, num, step=1):
        """Function to make Recursive Elimination and get best features.

        Args: 
            num (int) Number of features to select.
            step (float) How many features to eliminate in each fit.

        Returns: 
            plot best correlation the best features are assigned rank 1.

        """
        estimator = SVR(kernel="linear")
        X = self.x
        y = self.y
        selector = RFE(estimator, n_features_to_select=num, step=step)
        selector.fit(X, y)
        importances = pd.Series(data=selector.ranking_, index=X.columns)
        sns.barplot(x=importances, y=importances.index, orient="h").set_title(
            "Importância de cada feature"
        )