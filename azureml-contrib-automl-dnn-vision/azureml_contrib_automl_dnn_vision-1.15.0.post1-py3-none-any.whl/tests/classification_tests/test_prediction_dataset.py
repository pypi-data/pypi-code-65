import pytest
from azureml.contrib.automl.dnn.vision.common.prediction_dataset import PredictionDataset
from azureml.contrib.automl.dnn.vision.common.labeled_dataset_helper import AmlLabeledDatasetHelper
from .aml_dataset_mock import AmlDatasetMock, WorkspaceMock, DataflowMock, DataflowStreamMock
import os
import pandas as pd


@pytest.mark.usefixtures('new_clean_dir')
class TestPredictionDataset:

    def test_prediction_dataset(self):
        test_dataset_id = 'e7c014ec-474a-49f4-8ae3-09049c701913'
        test_file0 = 'e7c014ec-474a-49f4-8ae3-09049c701913-1.txt'
        test_file1 = 'e7c014ec-474a-49f4-8ae3-09049c701913-2.txt'
        test_files = [test_file0, test_file1]
        test_files_full_path = [os.path.join(AmlLabeledDatasetHelper.get_data_dir(),
                                             test_file) for test_file in test_files]
        properties = {}
        label_dataset_data = {
            'Path': ['/' + f for f in test_files]
        }
        dataframe = pd.DataFrame(label_dataset_data)

        mockdataflowstream = DataflowStreamMock(test_files_full_path)
        mockdataflow = DataflowMock(dataframe, mockdataflowstream, 'Path')
        mockdataset = AmlDatasetMock(properties, mockdataflow, test_dataset_id)
        mockworkspace = WorkspaceMock(mockdataset)

        try:
            datasetwrapper = PredictionDataset(input_dataset_id=test_dataset_id, ws=mockworkspace,
                                               datasetclass=AmlDatasetMock)

            file_names = datasetwrapper._files
            file_names.sort()
            assert file_names == test_files, "File Names"
            assert len(datasetwrapper) == len(test_files), "len"

            for test_file in test_files_full_path:
                assert os.path.exists(test_file)

        finally:
            for test_file in test_files_full_path:
                os.remove(test_file)
