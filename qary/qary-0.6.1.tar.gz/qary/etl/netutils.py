""" Transformer based chatbot dialog engine for answering questions """
import logging
import os
import urllib
from pathlib import Path

from tqdm import tqdm
import dotenv
import boto3

from qary.constants import LARGE_FILES, DATA_DIR


log = logging.getLogger(__name__)


class DownloadProgressBar(tqdm):
    """ Utility class that adds tqdm progress bar to urllib.request.urlretrieve

    >>> filemeta = LARGE_FILES['floyd']
    >>> filename = Path(filemeta['path']).name
    >>> url  = filemeta['url']
    >>> dest_path  = str(Path(filemeta['path']))
    >>> with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as dpb:
    ...     urllib.request.urlretrieve(url, filename=dest_path, reporthook=dpb.update_to)
    ('...qary/data/corpora/wikipedia/floyd.pkl', <http.client.HTTPMessage...>)
    """

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_if_necessary(
        url_or_name,
        dest_path=None):
    file_meta = LARGE_FILES.get(url_or_name) or {'url': url_or_name}
    url = file_meta['url']
    dest_path = dest_path or file_meta.get('path')
    # TODO: walk down from URL filename to match up with directories in DATA_DIR to build dest path
    if not dest_path:
        dest_path = file_meta.get('path', Path(DATA_DIR, file_meta.get('filename', Path(url).name)))
    filename = Path(dest_path).name
    if Path(dest_path).is_file():
        return dest_path
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as dpb:
        try:
            urllib.request.urlretrieve(url, filename=dest_path, reporthook=dpb.update_to)
        except (urllib.error.HTTPError, ValueError):
            log.error(f'Unable to download file from "{url}" to "{dest_path}" using file_meta: {file_meta}.')
            return None
    return dest_path


HOME = os.path.expanduser('~')

for p in '.env/digitalocean-nlpia.org/.env.prod', f'{HOME}.env/digitalocean-nlpia.org/.env.prod':
    if os.path.isfile(p):
        dotenv.load_dotenv('.env/digitalocean-nlpia.org/.env.prod')
    else:
        dotenv.load_dotenv()


def connect(
        access_key_id=os.getenv('DO_ACCESS_KEY'),
        secret_access_key=os.getenv('DO_ACCESS_SECRET'),
        region_name='sfo2',
        spaces_name='tan',
        url=None):

    url = url or f'https://{spaces_name}.{region_name}.digitaloceanspaces.com'
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='sfo2',
                            endpoint_url=url,
                            aws_access_key_id=access_key_id,
                            aws_secret_access_key=secret_access_key)
    return client


def ls():
    # need to have setup boto.cfg
    s3 = boto3.resource('s3')
    b = s3.Bucket('some/path/')
    # return list(b.objects.all())
    return list(b.objects.filter(Prefix='some/path'))


def upload_file(
        source='scripts/docs/*.pkl',
        dest=None,
        access_key_id=os.getenv('DO_ACCESS_KEY'),
        secret_access_key=os.getenv('DO_ACCESS_SECRET'),
        region_name='sfo2',
        spaces_name='tan',
        url=None):

    client = connect(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region_name=region_name,
        spaces_name=spaces_name,
        url=url)

    dest = dest or source
    retval = client.upload_file(source, spaces_name, dest)
    return retval
