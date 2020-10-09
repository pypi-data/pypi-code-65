import pandas as pd
from sklearn import metrics
from sklearn.externals import joblib
import json


def score(data_conf, model_conf, **kwargs):
    predict_df = pd.read_csv(data_conf['location'])
    features = 'sepallength,sepalwidth,petallength,petalwidth'.split(',')
    X_test = predict_df.loc[:, features]
    y_test = predict_df['class']

    model = joblib.load('artifacts/input/iris_knn.joblib')

    y_pred = model.predict(X_test)

    print("Finished Scoring")

    # store predictions somewhere.. As this is demo, we'll just print to stdout.
    print(y_pred)

    return X_test, y_pred, y_test, model


def save_plot(title):
    import matplotlib.pyplot as plt

    plt.title(title)
    fig = plt.gcf()
    filename = title.replace(" ", "_").lower()
    fig.savefig('artifacts/output/{}'.format(filename), dpi=500)


def evaluate(data_conf, model_conf, **kwargs):
    """Python evaluate method called by AOA framework

    Parameters:
    data_conf (dict): The dataset metadata
    model_conf (dict): The model configuration to use

    Returns:
    None:No return

    """

    X_test, y_pred, y_test, model = score(data_conf, model_conf, **kwargs)

    evaluation = {
        'Accuracy': '{:.2f}'.format(metrics.accuracy_score(y_test, y_pred)),
        'Recall': '{:.2f}'.format(metrics.recall_score(y_test, y_pred)),
        'Precision': '{:.2f}'.format(metrics.precision_score(y_test, y_pred)),
        'f1-score': '{:.2f}'.format(metrics.f1_score(y_test, y_pred))
    }

    with open("artifacts/output/metrics.json", "w+") as f:
        json.dump(evaluation, f)

    metrics.plot_confusion_matrix(model, X_test, y_test)
    save_plot('Confusion Matrix')

    metrics.plot_roc_curve(model, X_test, y_test)
    save_plot('ROC Curve')

    print("Evaluation complete...")


# Uncomment this code if you want to deploy your model as a Web Service (Real-time / Interactive usage)
# class ModelScorer(object):
#    def __init__(self, config=None):
#        self.model = joblib.load('artifacts/input/iris_knn.joblib')
#
#    def predict(self, data):
#        return self.model.predict([data])
#