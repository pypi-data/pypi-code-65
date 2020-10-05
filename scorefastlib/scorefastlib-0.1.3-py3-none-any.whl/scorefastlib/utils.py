# -*- coding: utf-8 -*-
import os
import time
import requests
import boto3
import pickle
import collections
import subprocess
from gzip import GzipFile
from io import BytesIO
from scorefastlib.common.rest_client import RestClient
from scorefastlib.common.constants import Constant


def list_dataset():
    """ list dataset """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN
    dataset_ret = RestClient.get(
        url=Constant.dataset_url.value,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()
    if dataset_ret.get('status') != 'success':
        raise Exception("Failed to retrieve the list of dataset")
    return dataset_ret.get('data')

def read_dataset(dataset_id):
    """
    read the dataset

    :param dataset_id: The dataset id from platform
    :return: returns dataset content
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN
    dataset_url = os.path.join(Constant.dataset_url.value, dataset_id)
    dataset_ret = RestClient.get(
        url=dataset_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()
    if dataset_ret.get('status') != 'success':
        raise Exception("Failed to retrieve the list of dataset")
    data = dataset_ret.get('data')
    file_path = data.get('path')
    
    # due to deprecated api
    if not file_path.startswith('api'):
        file_path = os.path.join('api', file_path)
    file_download_path = os.path.join(Constant.root_url.value, file_path)

    file_path, ext = os.path.splitext(file_download_path)
    
    headers = {'Authorization': 'Token ' + AUTH_TOKEN}
    r = requests.get(file_download_path, allow_redirects=True, headers=headers)

    if ext == '.gz':
        bytestream = BytesIO(r.content)
        return GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
    else:
        return r.content.decode('utf-8')

def export_dataset(file_path, name, header=0,
    ignored_cols='', response_col='', tags='',
    privacy=0, license='other', parser_type='CSV', storage_config_id=1):
    """
    export dataset from notebook to console

    :param file_path: file path
    :param name: The name of dataset
    :param header: 0: No header, 1: header exists
    :param ignored_cols: Columns separated by comma eg. 'C1,C2,C3'
    :param response_col: Column for response
    :param tags: The list of tag
    :param privacy: 0: private, 1: public
    :param license: license name
    :param parser_type: CSV or TSV only
    :param storage_config_id: The id of storage config from the platform
    :return: returns nothing
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    data = _get_user_summary(token=AUTH_TOKEN)
    user_id = data.get('user_id')
    group_id = data.get('group_id', 1)

    # validate the name
    if not name:
        raise Exception("name is necessary")
    else:
        if parser_type == 'CSV':
            file_name = '{}.csv'.format(name)
        elif parser_type == 'TSV':
            file_name = '{}.tsv'.format(name)
        else:
            raise Exception("Not supporting data format {}. only support CSV or TSV".format(parser_type))

    # upload dataset to S3 after change the name
    if not file_path:
        raise Exception("Failed to find the file_path {}".format(file_path))

    uuid = int(time.time() * 1000000)
    file_size = os.path.getsize(file_path)
    s3_namespace = "{}/customer/{}/{}/{}".format(
        Constant.s3_environment.value,
        group_id,
        uuid,
        file_name)
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        file_path, Constant.s3_bucket.value, s3_namespace)

    # get sample dataset
    sample_dataset = _parse_dataset(
        token=AUTH_TOKEN,
        storage_id=storage_config_id,
        url=s3_namespace)

    # get dataset meta
    dataset_meta = _get_dataset_meta(sample_dataset)

    request_params = {
        "header": header,
        "ignored_cols": ignored_cols,
        "response_col": response_col,
        "tags": tags,
        "vpredict": "1",
        "privacy": privacy,
        "license": license,
        "name": name,
        "file_array": [{"path": s3_namespace, "name": file_name, "fileSize": file_size}],
        "total_file_size": file_size,
        "parser_type": parser_type,
        "sample_data": sample_dataset,
        "meta": dataset_meta,
        "subtitle": "",
        "description": "",
        "storage_config_id": storage_config_id
    }
    res = _post_dataset(token=AUTH_TOKEN, request_params=request_params)
    return str(res)

def _post_dataset(token, request_params):
    """ post dataset """
    dataset_ret = RestClient.post(
        url=Constant.dataset_import_url.value,
        headers={'Authorization': 'Token ' + token},
        data=request_params).json()

    if dataset_ret.get('status') != 'success':
        raise Exception("Failed to post the dataset")
    return dataset_ret.get('pk')

def _get_dataset_meta(sample_dataset):
    """ get datatset meta information """
    dataset_meta = {}
    mapping_desc = {}
    mapping_type = {}
    header = sample_dataset.split("\n")[0]
    header_list = header.split(",")
    for i, column_name in enumerate(header_list):
        mapping_desc[str(i)] = ""
        mapping_type[str(i)] = "auto"
    dataset_meta['column_desc'] = mapping_desc
    dataset_meta['column_type'] = mapping_type
    return dataset_meta

def import_model(build_id):
    """
    read the python model

    :param build_id: build id from the platform
    :return: returns pickle model
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    headers = {'Authorization': 'Token ' + AUTH_TOKEN}
    url = os.path.join(Constant.model_download_url.value, "{}".format(build_id))
    r = requests.get(url, allow_redirects=True, headers=headers)
    file_path = "/tmp/{}.pkl".format(build_id)
    open(file_path, 'wb').write(r.content)
    loaded_model = pickle.load(open(file_path, 'rb'))
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise Exception("Failed to retrieve the model")
    return loaded_model

def _parse_dataset(token, storage_id, url):
    """ parse dataset """
    request_params = {
        "file_path": url,
        "range_start": 0,
        "range_end": 10485760,
        "storage_id": storage_id
    }

    dataset_parse_ret = RestClient.post(
        url=Constant.dataset_parse_url.value,
        headers={'Authorization': 'Token ' + token},
        data=request_params).json()

    if dataset_parse_ret.get('status') != 'success':
        raise Exception("Failed to parse the dataset")
    return dataset_parse_ret.get('data')

def _get_user_summary(token):
    """ get user meta information """
    user_summary_ret = RestClient.get(
        url=Constant.user_summary_url.value,
        headers={'Authorization': 'Token ' + token}).json()
    if user_summary_ret.get('status') != 'success':
        raise Exception("Failed to retrieve the user summary")
    return user_summary_ret.get('data')

def deploy_model(model, name, dataset_id=None, algorithm=None, build_id=None):
    """
    deploy the model

    :param model: python classifier
    :param name: The name of the model will show in the platform
    :param dataset_id: The id of dataset
    :param algorithm: Custom algorithm name
    :param build_id: build id in order to predict, otherwise, it will be random
    :return: returns nothing
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    data = _get_user_summary(token=AUTH_TOKEN)
    user_id = data.get('user_id')
    group_id = data.get('group_id', 1)
    
    # create pickle
    directory = os.path.join('/tmp', str(group_id))
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = '{}.pkl'.format(name)
    file_path = '{}/{}'.format(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    pickle.dump(model, open(file_path, 'wb'))

    # upload the model to S3
    uuid = int(time.time() * 1000000)
    file_size = os.path.getsize(file_path)
    s3_namespace = "{}/customer/{}/{}/{}".format(
        Constant.s3_environment.value,
        group_id,
        uuid,
        file_name)
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        file_path, Constant.s3_bucket.value, s3_namespace)
    
    # ping API end point to set
    params = {
        "name": name,
        "type": 3,
        "dataset_id": dataset_id,
        "algorithm": algorithm,
        "file_array": [{
            "name": file_name,
            "file_size": file_size,
            "path": s3_namespace}]
    }

    if build_id:
        params['build_id'] = build_id

    model_import_ret = RestClient.post(
        url=Constant.model_import_url.value,
        headers={'Authorization': 'Token ' + AUTH_TOKEN},
        data=params).json()
    if model_import_ret.get('status') != 'success':
        raise Exception("Failed to deploy the model")

def sync_to_cloud():
    """
    sync_to_cloud
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    data = _get_user_summary(token=AUTH_TOKEN)
    user_id = data.get('user_id')
    dest = "s3://{}/notebook/{}/{}".format(
        Constant.s3_bucket.value,
        Constant.s3_environment.value,
        user_id)
    subprocess.run(["aws", "s3", "sync", "/work_directory", dest], check=True)

def deploy_model_(model, name, dataset_id, algorithm=None, build_id=None):
    """
    deploy the model
    :param model: python model
    :param name: The name of the model will show in the platform
    :param dataset_id: The id of dataset, used for building the model, from platform
    :param algorithm: Custom algorithm name
    :param build_id: build id in order to predict, otherwise, it will be random
    :return: returns nothing
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    data = _get_user_summary(token=AUTH_TOKEN)
    user_id = data.get('user_id')
    group_id = data.get('group_id', 1)
    
    # create pickle
    directory = os.path.join('/tmp', str(group_id))
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = '{}.pkl'.format(name)
    file_path = '{}/{}'.format(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    pickle.dump(model, open(file_path, 'wb'))

    # upload the model to S3
    uuid = int(time.time() * 1000000)
    file_size = os.path.getsize(file_path)
    s3_namespace = "{}/customer/{}/{}/{}".format(
        Constant.s3_environment.value,
        group_id,
        uuid,
        file_name)
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        file_path, Constant.s3_bucket.value, s3_namespace)
    
    # ping API end point to set
    params = {
        "name": name,
        "type": 3,
        "dataset_id": dataset_id,
        "algorithm": algorithm,
        "file_array": [{
            "name": file_name,
            "file_size": file_size,
            "path": s3_namespace}]
    }

    if build_id:
        params['build_id'] = build_id

    model_import_ret = RestClient.post(
        url=Constant.model_import_url.value,
        headers={'Authorization': 'Token ' + AUTH_TOKEN},
        data=params).json()
    if model_import_ret.get('status') != 'success':
        raise Exception("Failed to deploy the model")

def list_project():
    """ list projects """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN
    project_ret = RestClient.get(
        url=Constant.project_url.value,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()
    if project_ret.get('status') != 'success':
        raise Exception("Failed to retrieve the list of projects")
    return project_ret.get('data')

def get_project_content(project_id, datasets=True, models=True, files=True):
    """ accessing content of a project
    :param project_id: The project id from platform
    :param datasets: boolean, optional, default True. Set to false to ignore list of the datasets in the project
    :param models: boolean, optional, default True. Set to false to ignore list of the models in the project
    :param files: boolean, optional, default True. Set to false to ignore list of the files in the project

    :return: returns contents of the project in a python dictionary format
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    response = {}
    response['project_id'] = project_id
    project_url = os.path.join(Constant.project_url.value, str(project_id))
    project_ret = RestClient.get(
        url=project_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()

    if project_ret.get('status') != 'success':
        raise Exception("Failed to access project_id : {}".format(project_id))

    response['project_name'] = project_ret['data']['name']

    if datasets:

        datasets_url = os.path.join(project_url,'dataset')
        dataset_ret = RestClient.get(
        url=datasets_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()
        if dataset_ret.get('status') != 'success':
            raise Exception("Failed to access project_id : {}'s datasets".format(project_id))

        response['datasets'] = dataset_ret.get('data')

    if models:

        model_url = os.path.join(project_url,'model')
        model_ret = RestClient.get(
        url=model_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()
        if model_ret.get('status') != 'success':
            raise Exception("Failed to access project_id : {}'s models".format(project_id))

        response['models'] = model_ret.get('data')

    if files:

        file_url = os.path.join(project_url,'file')
        file_ret = RestClient.get(
        url=file_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()
        if file_ret.get('status') != 'success':
            raise Exception("Failed to access project_id : {}'s files".format(project_id))

        response['files'] = file_ret.get('data')

    return response


def download_file_from_project(project_id, file_name=None):
    """
    download project files into local resource
    :param project_id: Id of the project assosiated with the requested file from platform
    :param file_name: string, default None, optional. The file name from platform. If not passed all the files in the project will be downloaded

    :return: downloaded files' path in local resource
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    project_file_url = os.path.join(Constant.project_url.value, str(project_id), 'file')
    project_file_ret = RestClient.get(
        url=project_file_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN}).json()

    if project_file_ret.get('status') != 'success':
        raise Exception("Failed to access project_id : {}'s files".format(project_id))

    if file_name:
        file_download_path = ''
        file_size = 0
        file_list = project_file_ret.get('data')
        for file in file_list:
            if file['name'] == file_name:
                file_download_path = file.get('path')
                file_size = file.get('file_size')
                break

        if len(file_download_path) == 0:
            raise Exception("Failed to find file {} in project {}".format(file_name, project_id))

        file_download_url = os.path.join(Constant.root_url.value, file_download_path)
        local_path = _download_file(project_id, file_download_url, file_name, file_size)
        return 'successfully downloaded file to {}'.format(local_path)

    local_paths = []
    file_list = project_file_ret.get('data')
    for file in file_list:
        file_download_path = file.get('path')
        file_size = file.get('file_size')
        file_name = file.get('name')
        file_download_url = os.path.join(Constant.root_url.value, file_download_path)
        local_path = _download_file(project_id, file_download_url, file_name, file_size)
        local_paths.append(local_path)
    directory = '/tmp/{}'.format(str(project_id))

    return 'successfully downloaded project {} files to {}'.format(project_id, directory)

def _download_file(project_id, file_download_url, file_name, file_size):
    """ download a file from project"""
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    file_download_ret = RestClient.get(
        url=file_download_url,
        headers={'Authorization': 'Token ' + AUTH_TOKEN})
    if str(file_download_ret.status_code) != '200':
        raise Exception("Failed to download file {}".format(file_name))

    directory = os.path.join('/tmp', str(project_id))
    if not os.path.exists(directory):
        os.makedirs(directory)
    local_path = '{}/{}'.format(directory, file_name)
    with open(local_path, 'w+b') as local:
        local.write(file_download_ret.content)

    if file_size != os.path.getsize(local_path):
        raise Exception("Failed to download file {}".format(file_name))

    return local_path

def upload_file_to_project(project_id, file_path, file_name):
    """
    upload a file from local resurce to a project on platform

    :param project_id: Id of the destination project from platform
    :param file_path: string. The local file path
    :param file_name: string. Name of the file on the platform

    :return: id of the datafile
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    data = _get_user_summary(token=AUTH_TOKEN)
    user_id = data.get('user_id')
    group_id = data.get('group_id', 1)
    # upload the file to S3
    uuid = int(time.time() * 1000000)
    file_size = os.path.getsize(file_path)
    s3_namespace = "{}/customer/{}/{}/{}".format(
        Constant.s3_environment.value,
        group_id,
        uuid,
        file_name)
    s3_client = boto3.client('s3')
    s3_client.upload_file(
        file_path, Constant.s3_bucket.value, s3_namespace)

    headers = {'Authorization': 'Token ' + AUTH_TOKEN}
    payload = {"project_id":project_id,
                "path":s3_namespace,
                "file_size":file_size,
                "name":file_name}

    file_ret = RestClient.post(
            url=Constant.file_url.value,
            headers=headers,
            data=payload).json()

    if file_ret.get('status') != 'success':
        raise Exception("Failed to upload_file {} to project_id {}".format(file_name, project_id))

    return 'successfully uploaded file {} to project_id {} with datafile id {}'.\
                                format(file_name,project_id,file_ret['data']['id'])

def sync_to_cloud__():
    """
    sync_to_cloud
    """
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN', '')
    assert AUTH_TOKEN

    data = _get_user_summary(token=AUTH_TOKEN)
  
    user_id = data.get('user_id')
    dest = "s3://{}/notebook/{}/{}".format(
        Constant.s3_bucket.value,
        Constant.s3_environment.value,
        user_id)
    
    subprocess.run(["aws", "s3", "sync", "/work_directory", dest, "--exclude", '*', "--include", '*.ipynb'], check=True)
        

if __name__ == '__main__':
    read_dataset("1377")
    set_model("", name="finalized_model")
