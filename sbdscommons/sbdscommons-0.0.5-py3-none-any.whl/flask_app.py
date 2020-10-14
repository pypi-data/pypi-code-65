import pickle
from io import StringIO

import flask
import pandas as pd
from flask import Flask
from flask import Response
from sbcommons.logging.lambda_logger import get_logger

from sbdscommons.sbdscommons.model.model import SbModel

app = Flask(__name__)
logger = get_logger(__name__)


def load_model() -> SbModel:
    with open('/opt/ml/model/sb_model.pickle', 'rb') as handle:
        sb_model: SbModel = pickle.load(handle)
        logger.info(f'Loaded model {sb_model} using pickle on docker')
        return sb_model


@app.route('/ping', methods=['GET'])
def ping() -> Response:
    """
    Determine if the container is healthy by running a sample through the algorithm.
    """
    sb_model = load_model()
    predict_input_sample = pd.read_csv('tests/data/sample_model_input_prediction.csv',
                                       sep='|',
                                       quotechar='"')

    try:
        sb_model.predict(predict_input_sample)
        return Response(response='{"status": "ok"}', status=200, mimetype='application/json')
    except Exception as e:
        logger.exception(f'Unknown exception of type {e.__class__.__name__} occurred.')
        return Response(response='{"status": "error"}', status=500, mimetype='application/json')


@app.route('/execution-parameters', methods=['GET'])
def execution_parameters() -> Response:
    """
    SageMaker sets environment variables
    SAGEMAKER_MAX_PAYLOAD_IN_MB is set to the largest size payload that will be sent to the container via HTTP.

    SAGEMAKER_BATCH_STRATEGY will be set to SINGLE_RECORD when the container will be sent a single record per call to invocations and MULTI_RECORD when the container will get as many records as will fit in the payload.

    SAGEMAKER_MAX_CONCURRENT_TRANSFORMS is set to the maximum number of /invocations requests that can be opened simultaneously.

    """
    logger.info('execution-parameters function')
    return Response(response='{"status": "ok"}', status=200, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def predict() -> Response:
    """
    Do an inference on a single batch of data.
    """
    if flask.request.content_type == 'text/csv':
        predict_data = flask.request.data.decode('utf-8')
        buffer = StringIO()
        buffer.write(predict_data)
        buffer.seek(0)
        predict_input = pd.read_csv(buffer, sep='|', quotechar='"')
    else:
        return flask.Response(response='This predictor only supports CSV data', status=415,
                              mimetype='text/plain')

    sb_model = load_model()
    predict_data = sb_model.predict(predict_input)
    out = StringIO()
    predict_data.to_csv(out, sep='|', quotechar='"', index=False)
    results_str = out.getvalue()
    return Response(response=results_str, status=200, mimetype='text/csv')
