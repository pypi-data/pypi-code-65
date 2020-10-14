# ==========================
# AWS CONSTANTS
# ==========================
import os

ENV = 'prod'
ROLE = 'arn:aws:iam::485206745971:role/service-role/AmazonSageMaker-ExecutionRole-20190528T144422'
ACCOUNT = '485206745971'
REGION = 'eu-north-1'
BUCKET = f'sb-data-sc-{ENV}'

# Absolute path to folder with model params
PARAMS_FOLDER = f'{os.path.dirname(os.path.abspath(__file__))}/params'

# Model paths
INPUT_TRAIN_PATH_FMT = '{MODEL_NAME}/input_data/train'
INPUT_PREDICT_PATH_FMT = '{MODEL_NAME}/input_data/predict'
OUTPUT_PATH_FMT = '{MODEL_NAME}/output_data'
MODEL_PATH_FMT = '{MODEL_NAME}/model'
