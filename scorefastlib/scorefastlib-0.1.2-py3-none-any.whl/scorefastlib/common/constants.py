# -*- coding: utf-8 -*-
import enum


class Constant(enum.Enum):
    """ constant """
    root_url = "https://develop.scoredata.com"
    dataset_url = "{}/api/imported_data/".format(root_url)
    dataset_download_url = "{}/api/dataset/download/".format(root_url)
    model_download_url = "{}/api/model/download".format(root_url)
    model_url = "{}/api/model/".format(root_url)
    model_import_url = "{}/api/model/import/".format(root_url)
    user_summary_url = "{}/api/user/summary/".format(root_url)
    dataset_parse_url = "{}/api/dataset/parse/".format(root_url)
    dataset_import_url = "{}/api/imported_data/".format(root_url)
    project_url = "{}/api/project/".format(root_url)
    file_url = "{}/api/file/".format(root_url)
    
    s3_bucket = "scoredata-us-west1-data"
    s3_environment = "QA"
