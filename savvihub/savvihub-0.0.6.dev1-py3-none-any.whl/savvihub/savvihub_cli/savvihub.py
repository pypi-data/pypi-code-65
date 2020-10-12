import requests
import typing

from savvihub.savvihub_cli.constants import HOST_URL
from savvihub.savvihub_cli.utils import AnnotatedObject


class SavviDatasetFile(AnnotatedObject):
    path: str
    is_dir: bool

    size: int
    hash: str

    download_url: str
    upload_url: str


class SavviExperimentArtifact(AnnotatedObject):
    path: str
    is_dir: bool

    size: int
    hash: str

    download_url: str
    upload_url: str


class SavviKernelImage(AnnotatedObject):
    id: int
    image_url: str
    name: str


class SavviKernelResource(AnnotatedObject):
    id: int
    name: str
    cpu_limit: float
    mem_limit: str


class SavviDataset(AnnotatedObject):
    id: int
    name: str


class SavviListResponse(AnnotatedObject):
    results: typing.List


class PaginatedMixin(AnnotatedObject):
    total: int
    startCursor: typing.Optional[str]
    endCursor: typing.Optional[str]
    results: typing.List


class SavviHubPaginatedDatasetFilesResponse(PaginatedMixin, AnnotatedObject):
    results: typing.List[SavviDatasetFile]


class SavviHubClient:
    def __init__(self, *, session=requests.Session(), token=None, url=HOST_URL, content_type='application/json'):
        self.session = session
        self.url = url
        self.token = token
        
        session.headers = {'content-type': content_type}
        if token:
            session.headers['authorization'] = 'Token %s' % token

    def get(self, url, params=None, raise_error=False, **kwargs):
        r = self.session.get(f'{self.url}{url}', params=params, **kwargs)
        if raise_error:
            r.raise_for_status()
        return r

    def get_all(self, url, params=None, raise_error=False, **kwargs):
        raw_resp = self.get(url, params=params, raise_error=raise_error, **kwargs)
        resp = PaginatedMixin(raw_resp.json())
        results = []

        fetched_items = 0
        while True:
            fetched_items += len(resp.results)
            results.extend(resp.results)
            if fetched_items >= resp.total:
                break
            raw_resp = self.get(url, params={**params, 'after': resp.endCursor}, raise_error=raise_error, **kwargs)
            resp = PaginatedMixin(raw_resp.json())
        return results

    def get_all_without_pagination(self, url, params=None, raise_error=False, **kwargs):
        raw_resp = self.get(url, params=params, raise_error=raise_error, **kwargs)
        resp = SavviListResponse(raw_resp.json())
        return resp.results

    def post(self, url, data, raise_error=False, **kwargs):
        r = self.session.post(f'{self.url}{url}', json=data, **kwargs)
        if raise_error:
            r.raise_for_status()
        return r

    def delete(self, url, raise_error=False, **kwargs):
        r = self.session.delete(f'{self.url}{url}', **kwargs)
        if raise_error:
            r.raise_for_status()
        return r

    def patch(self, url, data, raise_error=False, **kwargs):
        r = self.session.patch(f'{self.url}{url}', json=data, **kwargs)
        if raise_error:
            r.raise_for_status()
        return r

    def dataset_file_list(self, workspace, dataset, *, ref='latest', **kwargs) -> typing.List[SavviDatasetFile]:
        results = self.get_all(f'/v1/api/workspaces/{workspace}/datasets/{dataset}/files/', params={'ref': ref}, **kwargs)
        return [SavviDatasetFile(x) for x in results]

    def dataset_file_create(self, workspace, dataset, path, is_dir, **kwargs):
        return self.post(f'/v1/api/workspaces/{workspace}/datasets/{dataset}/files/', {
            'path': path,
            'is_dir': is_dir
        }, **kwargs)

    def experiment_read(self, **kwargs):
        return self.get(f'/v1/api/experiments/', **kwargs)

    def experiment_list(self, workspace, project, **kwargs):
        return self.get(f'/v1/api/workspaces/{workspace}/projects/{project}/experiments/?orderby.direction=DESC', **kwargs)

    def experiment_log(self, workspace, project, experiment_number, **kwargs):
        return self.get(f'/v1/api/workspaces/{workspace}/projects/{project}/experiments/{experiment_number}/log/', **kwargs)

    def experiment_create(self, workspace, project, image_id, resource_spec_id, branch, dataset_mount_infos, start_command, **kwargs):
        return self.post(f'/v1/api/workspaces/{workspace}/projects/{project}/experiments/', {
            'image_id': image_id,
            'resource_spec_id': resource_spec_id,
            'branch': branch,
            'dataset_mount_infos': dataset_mount_infos,
            'start_command': start_command,
        }, **kwargs)

    def experiment_progress_update(self, experiment_id, row, **kwargs):
        return self.post(f'/v1/api/experiments/{experiment_id}/progress/', {
            'metrics': [row],
        }, **kwargs)

    def experiment_artifact_create(self, experiment_id, path, **kwargs):
        return self.post(f'/v1/api/experiments/{experiment_id}/artifacts/', {
            'path': path,
            'is_dir': False,
        }, **kwargs)

    def kernel_image_list(self, workspace):
        results = self.get_all_without_pagination(f'/v1/api/workspaces/{workspace}/kernels/images/')
        return [SavviKernelImage(x) for x in results]

    def kernel_resource_list(self, workspace):
        results = self.get_all_without_pagination(f'/v1/api/workspaces/{workspace}/kernels/resource_specs')
        return [SavviKernelResource(x) for x in results]

    def public_dataset_list(self):
        results = self.get_all(f'/v1/api/datasets/public/')
        return [SavviDataset(x) for x in results]

    def dataset_list(self, workspace):
        results = self.get_all(f'/v1/api/workspaces/{workspace}/datasets/')
        if not results:
            return []
        return [SavviDataset(x) for x in results]
