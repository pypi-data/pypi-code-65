import sys
import os
import glob
import shutil
import tempfile
from urllib.parse import urljoin
from getpass import getpass
from subprocess import Popen, PIPE, check_call
import requests
from scrapy.utils.conf import get_config, closest_scrapy_cfg
from scrapy.utils.python import retry_on_eintr
from . import CommandBase
from .package import _create_default_setup_py


def _build_egg():
    closest = closest_scrapy_cfg()
    os.chdir(os.path.dirname(closest))
    if not os.path.exists('setup.py'):
        settings = get_config().get('settings', 'default')
        _create_default_setup_py(settings=settings)
    d = tempfile.mkdtemp(prefix="scrapydeploy-")
    o = open(os.path.join(d, "stdout"), "wb")
    e = open(os.path.join(d, "stderr"), "wb")
    retry_on_eintr(check_call, [sys.executable, 'setup.py', 'clean', '-a', 'bdist_egg', '-d', d],
                   stdout=o, stderr=e)
    o.close()
    e.close()
    egg = glob.glob(os.path.join(d, '*.egg'))[0]
    return egg, d


def _get_targets():
    cfg = get_config()
    baset = dict(cfg.items('deploy')) if cfg.has_section('deploy') else {}
    targets = {}
    if 'url' in baset:
        targets['default'] = baset
    for x in cfg.sections():
        if x.startswith('deploy:'):
            t = baset.copy()
            t.update(cfg.items(x))
            targets[x[7:]] = t
    return targets


def _upload_egg(target, project_name=None, version=None, egg=None, auth=None):
    target = _get_targets()[target]
    base_url = target['url']
    session = requests.Session()
    session.auth = auth
    post_url = urljoin(base_url, 'addversion.json')
    if not project_name:
        project_name = target['project']
    if not version:
        version = '1.0'

    f_egg = open(egg, 'rb')
    response = session.post(post_url, data={
        'project': project_name, 
        'version': '1.0'
    }, files={'egg': f_egg})
    f_egg.close()
    response.raise_for_status()
    return response.json()



class DeployCommand(CommandBase):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--project', dest='project')

    def run(self, args):
        tmpdir = None
        egg, tmpdir = _build_egg()
        username = None
        password = None

        if not username:
            username = input("Username:\r\n")
        if not password:
            password = getpass('Password:\r\n')

        auth = requests.auth.HTTPBasicAuth(username, password)
        ret = _upload_egg('default', egg=egg, auth=auth, project_name=args.project)
        print(ret)

        if tmpdir:
            shutil.rmtree(tmpdir)
