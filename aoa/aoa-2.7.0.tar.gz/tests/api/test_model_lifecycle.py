import pytest

from aoa.api.job_api import JobApi
from aoa.api.trained_model_api import TrainedModelApi
from aoa.api.deployment_api import DeploymentApi

max_retries = 10


@pytest.mark.xfail
def test_model_lifecycle(setup):
    trained_model_api = TrainedModelApi(pytest.aoa_client)
    job_api = JobApi(pytest.aoa_client)
    deployment_api = DeploymentApi(pytest.aoa_client)

    # Train
    training_request = dict()
    model_id = '03c9a01f-bd46-4e7c-9a60-4282039094e6'
    training_request['modelId'] = model_id
    training_request['datasetId'] = '11e1df4b-b630-47a1-ab80-7ad5385fcd8c'

    job_rtn = trained_model_api.train(training_request)
    job_id = job_rtn['id']
    job_rtn_by_id = job_api.find_by_id(job_id=job_id)

    assert (job_rtn_by_id['metadata']['trainingRequest'] == training_request), "validate training request...failed"

    job_api.wait(job_id)

    trained_model_id = job_rtn_by_id['metadata']['trainedModel']['id']
    trained_model_by_id = trained_model_api.find_by_id(trained_model_id=trained_model_id,
                                                       projection="expandTrainedModel")
    assert (trained_model_by_id['modelId'] == training_request['modelId'] and
            trained_model_by_id['dataset']['id'] == training_request['datasetId']), "train model...failed"

    # Evaluate
    evaluation_request = dict()
    evaluation_request['datasetId'] = '11e1df4b-b630-47a1-ab80-7ad5385fcd8c'

    job_eval_rtn = trained_model_api.evaluate(trained_model_id, evaluation_request)
    job_eval_id = job_eval_rtn['id']
    job_eval_rtn_by_id = job_api.find_by_id(job_id=job_eval_id)

    assert (job_eval_rtn_by_id['metadata']['evaluationRequest'] == evaluation_request), \
        "validate evaluate request...failed"

    job_api.wait(job_eval_id)

    trained_model_eval_by_id = trained_model_api.find_by_id(trained_model_id=trained_model_id,
                                                            projection="expandTrainedModel")
    assert (trained_model_eval_by_id['dataset']['id'] == evaluation_request['datasetId']), "evaluate model...failed"

    # Deploy

    deployment_engine_type = 'RESTFUL'
    job_deployed = trained_model_api.deploy(trained_model_id, deployment_engine_type)
    job_api.wait(job_deployed['id'])
    assert('type' in job_deployed and job_deployed['type'] == 'DEPLOYMENT'), "Deployment job has not been scheduled"

    deployed_status = trained_model_api.find_by_model_id_and_status(model_id=model_id, status="DEPLOYED")
    assert (1 == deployed_status['page']['totalElements']), "Model has not been deployed"

    # Deployment

    deployment = deployment_api.find_active_by_trained_model_and_engine_type(trained_model_id=trained_model_id,
                                                                             engine_type=deployment_engine_type)
    assert ('status' in deployment and deployment['status'] == 'DEPLOYED'), "Deployment doesn't show up in Deployment API"

    # Retire

    job_retired = trained_model_api.retire(trained_model_id, deployment['id'])
    job_api.wait(job_retired['id'])
    assert('type' in job_retired and job_retired['type'] == 'RETIREMENT'), "Retirement job has not been scheduled"

    retired_status = trained_model_api.find_by_model_id_and_status(model_id=model_id, status="RETIRED")
    assert (1 == retired_status['page']['totalElements']), "Model has not been retired"
