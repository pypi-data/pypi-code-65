import json
import logging
import os

from fastapi.encoders import jsonable_encoder

from .accuracy import calibration, largest_errors, metrics
from .dependence import partialdep
from .expectations import condexp
from .importance import varimp
from .shap import ShapExplainer
from .utils import create_description, df_to_dict


def create_shapley_schema(endpoint, basepath="results"):
    """Create shapley schema for endpoint"""
    name = endpoint.func.__name__
    explainer = ShapExplainer(func=endpoint.func, X=endpoint.X)
    folder = os.path.join(basepath, endpoint.func.__name__)
    input_descriptions = [create_description(endpoint.X[col]) for col in endpoint.X]
    if not os.path.exists(folder):
        os.makedirs(folder)

    logging.info("Shapley - Creating schema")
    fname = "schema.json"
    fpath = os.path.join(folder, fname)
    data = create_explainer_schema(endpoint, explainer, input_descriptions)
    with open(fpath, "w") as f:
        json.dump(jsonable_encoder(data), f)


def create_explainer_schema(endpoint, explainer, input_descriptions):
    """Create schema for explainer input"""
    # create an example
    name = endpoint.func.__name__
    X = endpoint.X.sample(n=1)
    pred = endpoint.func(X)
    baseline, explanation = explainer.explain(X)
    example = {
        "inputs": df_to_dict(X),
        "explanations": df_to_dict(explanation),
        "prediction": list(pred),
        "baseline": list(baseline),
    }
    # build schema
    schema = {"input_descriptions": input_descriptions, "example": example}
    return schema


def create_accuracy(endpoint, basepath="results"):
    """Create accuracy profile for endpoint"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y

    kind = endpoint.kind
    folder = os.path.join(basepath, func.__name__, "accuracy")
    if not os.path.exists(folder):
        os.makedirs(folder)

    logging.info("Accuracy - Creating calibration plot")
    fname = "calibration.json"
    fpath = os.path.join(folder, fname)
    chart = calibration(func, X, y)
    chart.save(fpath, format="json")

    logging.info("Accuracy - Creating metrics table")
    fname = "metrics.json"
    fpath = os.path.join(folder, fname)
    metrics_table = metrics(func, X, y, kind)
    with open(fpath, "w") as f:
        f.write(metrics_table)

    logging.info("Accuracy - Finding largest errors")
    fname = "errors.json"
    fpath = os.path.join(folder, fname)
    errors_table = largest_errors(func, X, y)
    with open(fpath, "w") as f:
        f.write(errors_table)


def create_dependence(endpoint, basepath="results"):
    """Create partial dependence graphs for all variables"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y
    folder = os.path.join(basepath, func.__name__, "anatomy", "partialdep")
    if not os.path.exists(folder):
        os.makedirs(folder)

    for var in X.columns:
        logging.info(f"Explanations - Creating partial dependence for {var}")
        fname = var + ".json"
        fpath = os.path.join(folder, fname)
        try:
            chart = partialdep(func, X, y, var)
            chart.save(fpath, format="json")
        except AttributeError:
            logging.warning(f"Could not generate valid chart for {var}")


def create_expectations(endpoint, basepath="results"):
    """Create conditional expectations graphs for all variables"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y
    folder = os.path.join(basepath, func.__name__, "anatomy", "condexp")
    if not os.path.exists(folder):
        os.makedirs(folder)

    for var in X.columns:
        logging.info(f"Explanations - Creating conditional expectations for {var}")
        fname = var + ".json"
        fpath = os.path.join(folder, fname)
        try:
            chart = condexp(func, X, y, var)
            chart.save(fpath, format="json")
        except AttributeError:
            logging.warning(f"Could not generate valid chart for {var}")


def create_importance(endpoint, basepath="results"):
    """Create variable importance graphs"""
    func = endpoint.func
    X = endpoint.X
    y = endpoint.y

    logging.info("Explanations - Calculating variable importance")
    if endpoint.kind == "regression":
        chart, varlist = varimp(func, X, y, metric="Rmse")
    elif endpoint.kind == "binary":
        chart, varlist = varimp(func, X, y, metric="AUC")
    else:
        raise NotImplementedError("Unknown endpoint kind:" + endpoint.kind)

    # Save to disk
    folder = os.path.join(basepath, func.__name__, "anatomy")
    if not os.path.exists(folder):
        os.makedirs(folder)

    fname = "varimp.json"
    fpath = os.path.join(folder, fname)
    chart.save(fpath, format="json")

    fname = "varlist.json"
    fpath = os.path.join(folder, fname)
    with open(fpath, "w") as f:
        json.dump(varlist, f)


def create_summary(endpoint, basepath="results"):
    endpoint_name = endpoint.func.__name__
    as_json = {
        "name": endpoint_name,
        "kind": endpoint.kind,
        "inputs": list(endpoint.X.columns),
        "output": endpoint.y.name,
    }
    with open(os.path.join(basepath, endpoint_name, "summary.json"), "w") as summary:
        json.dump(as_json, summary)
