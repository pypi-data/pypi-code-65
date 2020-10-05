import gzip
import os
import shutil
from datatransfer.rest_client import RestClient
from datatransfer import constants


class Utility:


    @staticmethod
    def __is_file_compressed(filename):
        is_file_compressed = False
        if filename.endswith(".gz") or filename.endswith(".gzip") or filename.endswith(".tar") \
                or filename.endswith(".zip") or filename.endswith("bz2")\
                or filename.endswith("xz") or filename.endswith("rar"):
            is_file_compressed = True
        return is_file_compressed

    @staticmethod
    def __compress_file__(path,compressed_path_dir, compress_type):

        if Utility.__is_file_compressed(path):
            return path
        if compress_type == "gz":
            compressed_path = os.path.join(compressed_path_dir,
                                           os.path.basename(path) + ".gz")
            with open(path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb',
                               compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return compressed_path
        else:
            return path

    @staticmethod
    def __authenticate_request__(user_name, password):

        token_res = RestClient.get(
            url=constants.Constant.score_token_url.value,
            auth={'user': user_name,
                  'password': password}).json()
        if token_res.get('status') != 'success':
            raise Exception("Unauthorized Request: %s" % str(token_res.get('detail')))
        token = token_res.get('token')
        s3_conf = RestClient.post(
            url=constants.Constant.score_s3_config_url.value,
            headers={'Authorization': 'Token ' + token},
            data={"token": token}).json()
        if token_res.get('status') != 'success':
            raise Exception("Unauthorized Request, Connect to admin")
        return s3_conf.get('data')
