import os
import tempfile
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
import sys
import time
import pickle

from azureml.core import Experiment
from azureml.core.run import _OfflineRun, Run
from azureml.train.automl import constants
from azureml.train.automl.run import AutoMLRun

import azureml
from azureml.contrib.automl.dnn.vision.classification.common.constants import ArtifactsLiterals
import azureml.contrib.automl.dnn.vision.classification.runner as runner


data_folder = 'classification_data/images'
labels_root = 'classification_data/'


def _get_settings(csv_file):
    return {
        # Only run 1 epoch to make the test faster
        'epochs': 1,
        'images_folder': '.',
        'labels_file': csv_file,
        'num_workers': 0,
        'seed': 47,
        'deterministic': True
    }


@pytest.mark.usefixtures('new_clean_dir')
@mock.patch.object(azureml._restclient.jasmine_client.JasmineClient, '__init__', lambda x, y, z, **kwargs: None)
@mock.patch.object(azureml._restclient.experiment_client.ExperimentClient, '__init__', lambda x, y, z, **kwargs: None)
@mock.patch('azureml._restclient.jasmine_client.JasmineClient', autospec=True)
@mock.patch('azureml._restclient.experiment_client.ExperimentClient', autospec=True)
@mock.patch('azureml._restclient.run_client.RunClient', autospec=True)
@mock.patch('azureml._restclient.metrics_client.MetricsClient', autospec=True)
def test_multiclassification_local_run(mock_metrics_client, mock_run_client,
                                       mock_experiment_client, mock_jasmine_client,
                                       monkeypatch):

    settings = _get_settings('multiclass.csv')

    with monkeypatch.context() as m:
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            m.setattr(sys, 'argv', ['runner.py', '--data-folder', data_folder, '--labels-file-root', labels_root])
            settings['output_dir'] = tmp_output_dir
            settings['task_type'] = constants.Tasks.IMAGE_CLASSIFICATION
            runner.run(settings)
            expected_output = os.path.join(tmp_output_dir, ArtifactsLiterals.MODEL_WRAPPER_PKL)
            assert os.path.exists(expected_output)

            time.sleep(2)
            # support resume
            resume_pkl_file = expected_output
            with open(resume_pkl_file, 'rb') as fp:
                resume_pkl_model = pickle.load(fp)
                optimizer = resume_pkl_model.model_wrapper.optimizer.state_dict()
                assert optimizer is not None
                lr_scheduler = resume_pkl_model.model_wrapper.lr_scheduler.lr_scheduler.state_dict()
                assert lr_scheduler is not None
                assert len(optimizer['param_groups']) == len(lr_scheduler['base_lrs'])

            # bad path + resume flag should fail
            mock_run = _OfflineRun()
            mock_workspace = MagicMock()
            mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))

            with patch.object(Run, 'get_context', return_value=mock_run):
                with patch.object(AutoMLRun, '_is_local', return_value=False):
                    with patch.object(Run, 'fail', return_value=False) as mock_fail:
                        settings['resume'] = expected_output + "_random"
                        runner.run(settings)
                        mock_fail.assert_called_once()
                        assert mock_fail.call_args[1]['error_details'].error_type == 'SystemError'

            settings['resume'] = expected_output
            m.setattr(ArtifactsLiterals, 'MODEL_WRAPPER_PKL', ArtifactsLiterals.MODEL_WRAPPER_PKL + "_after_resume")
            expected_output_resume = os.path.join(tmp_output_dir,
                                                  ArtifactsLiterals.MODEL_WRAPPER_PKL)
            runner.run(settings)
            assert os.path.exists(expected_output_resume)
