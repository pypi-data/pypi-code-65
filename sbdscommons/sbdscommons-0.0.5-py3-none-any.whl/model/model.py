from sagemaker import Session
from sagemaker.transformer import Transformer
from sbdscommons.utils.yaml_utils import load_from_yaml

from sbdscommons.sbdscommons.constants import BUCKET
from .base import Model
from .base import PrepInput


class SbModel:
    separator = '-'

    def __init__(self,
                 model_name: str,
                 model: Model,
                 input_prep: PrepInput,
                 model_version: str,
                 bucket: str = BUCKET
                 ):
        self.model = model
        self.model_id = f'{model_name}{self.separator}{model_version}'
        self.input_prep = input_prep
        self.model_name = model_name
        self.input_train_path = f'{model_name}/input_data/train'
        self.input_predict_path = f'{model_name}/input_data/predict'
        self.output_path = f'{model_name}/output_data'
        self.model_path = f'{model_name}/model'
        self.bucket = bucket

    def __repr__(self):
        return self.model_id

    @staticmethod
    def load_model_params(params_path):
        ops_dict = load_from_yaml(params_path, key='options_dict')
        qry_dict = load_from_yaml(params_path, key='query_dict')
        return qry_dict, ops_dict

    def train(self, train_input):
        transformed_input = self.input_prep.transform(train_input)
        self.model.fit(transformed_input)

    def predict(self, predict_input):
        transformed_input = self.input_prep.transform(predict_input)
        return self.model.predict(transformed_input)

    def unload_for_predit(self):
        pass

    def unload_for_predit(self):
        pass

    def batch_transform_job(self):
        # CREATE A batch prediction job
        data_location = f's3://{self.bucket}/{self.output_path}'

        clf_trans = Transformer(
            base_transform_job_name='Batch-Transform',
            model_name=self.model_id,  # insert model name here
            instance_count=2,
            instance_type='ml.m5.2xlarge',
            output_path=data_location,
            sagemaker_session=Session(),
            max_payload=100
        )

        # Get some input data for the batch prediction job
        predict_data_key = f'{self.input_predict_path}/model_input_prediction000.csv'
        predict_data_location = f's3://{self.bucket}/{predict_data_key}'
        # start the prediction job
        clf_trans.transform(
            predict_data_location,
            content_type='text/csv',
            split_type='Line'
        )

        # wait until prediction job is completed
        clf_trans.wait()
