#!/usr/bin/env python3
# -.- coding: utf-8 -.-
"""Handles all data-related features."""

from pathlib import Path
import functools
import json
import os

from munch import munchify, Munch
import requests

from omic.client import Client
from omic.global_ import GlobalClient
from omic.parallel import run_parallel 
from omic.util import strict_http_do, check_args, get_cloud, \
                      download_url, vfs_path_join

__copyright__ = 'Copyright © 2020 Omic'


class DataClient(Client):

    def create_bundle(
        self: object, 
        files: list, 
        vpath: str, 
        mode: str, 
        project: str, 
        name: str = None,
        safe: bool = False
    ) -> str:
        workload = [functools.partial(self.mount_data, rpath, vpath, mode, 
                                      project, safe) for rpath in files]
        file_ids = run_parallel(workload, batch_size=15)
        return self._hit(
            'post',
             endpoint='/data/bundle',
             qparams={
                'name': name,
                'mode': mode, 
                'project': project
            },
            json_body=file_ids
        )._id

    def mount_data(self, *args, **kwargs):
        return self.mount(*args, **kwargs)

    # NOTE:  Formally `mount_data`.
    def mount(self, rpath: str, vpath: str, mode: str, project: str, 
              safe: bool = False):
        # TODO:  Add a parameter to preserve structure of rpath 
        #        (under mount key).  Right now we have flattened `vpath`s.
        qparams = {
            'user': self.config.user, 
            'mode': mode,
            'project': project,
            'cmd': 'mount',
            'repr': 'file',
            'mode': mode,
            'vpath': vpath, 
            'rpath': rpath,
            'safe': safe
        }
        print('Mount data:', rpath, '->', vpath)
        return self._hit('post',
                         endpoint='/data',
                         qparams=qparams).id

    def ls(
        self, 
        vpath: str = './', 
        mode: str = 'public', 
        project: str = None,
        silent=False
    ):
        if not project:
            # Fetch current project from user if none exists.
            gclient = GlobalClient(self.config)
            project = gclient.retrieve_project().project._id
        files = self._hit(
            'get',
            endpoint='/data',
            qparams={
                'cmd': 'ls', 'vpath': vpath, 'mode': mode,
                'project': project,  
            }
        )
        print('files', files)
        for f in files:
            print(' >', f.vpath)
        return files
        
    def get_data(
        self, 
        _id,
        soft: bool = False
    ):
        return self.stat(soft=soft, _id=id)

    # NOTE:  Formally `get_data`.
    def stat(self, soft: bool = False, **kwargs) -> Munch:
        return self._hit(
            'get',
            endpoint='/data',
            qparams={'cmd': 'stat', **kwargs}
        ),
        soft=soft

    def cat(
        self, 
        filepath: str = None, 
        #content: object = None,
        vpath: str = '/',
        mode: str = 'public',
        project: str = None
    ):
        print('Uploading file to CyberTree...')
        '''
        if content:
            if isinstance(content, str):
                content = content.encode('utf-8')
            assert isinstance(content, bytes)
        else:
            assert filepath
            content = open(filepath, 'rb').read()
        '''
        # Get presigned URL to which to upload
        response = self._hit(
            'post', 
            endpoint='/data', 
            qparams={
                'cmd': 'cat',
                'mode': mode,
                'vpath': vpath,
                'project': project,
                'repr': 'file'
            }
        )
        # Upload file 
        f = open(filepath, 'rb').read()
        files = {'file': (filepath, f)}
        req = requests.Request(
            'POST', 
            response['url'], 
            data=response['fields'], 
            files=files
        )
        prepared = req.prepare()
        s = requests.Session()  
        s.send(prepared)

    def _download_file(
        self, 
        _id: str = None, 
        vpath: str = '/', 
        mode: str = 'public', 
        project: str = None, 
        repr: str = 'file',
        download_dir: str = './', 
        silent=False
    ) -> None:
        # Stat the file
        s = self.stat(_id=_id)
        # Setup local path location
        lp = s.vpath[len(vpath):]
        lp = lp[1:] if lp.startswith('/') else lp
        lp = vfs_path_join(download_dir, lp) 
        lp = str(Path(lp).resolve())
        ldirs, filename = os.path.split(lp)
        Path(ldirs).mkdir(parents=True, exist_ok=True)
        # Download file in parallel
        download_url(s.url, lp, silent=silent, desc=filename)

    def download(
        self, 
        vpath: str = None, 
        _id: str = None, 
        mode: str = 'public', 
        project: str = None, 
        download_dir: str = './', 
        silent=False
    ) -> None:
        assert _id or vpath
        if _id:
            self._download_file(_id, download_dir=download_dir)
            print('File download complete.')
            return
        for f in self.ls(vpath=vpath, mode=mode, project=project):
            try:
                self._download_file(_id=f._id, download_dir=download_dir)
            except Exception as ex:
                print('Could not download {}.'.format(f.name), ex)
                return
        print('Download complete.')

    def get_bundle(
        self, 
        _id: str = None, 
        name: str = None, 
        fulfill: bool = False, 
        recurse: bool = False,
        soft: bool = False
    ) -> str:
        return self._hit(
            'get', 
            endpoint='/data/bundle', 
            qparams={
                '_id': _id,
                'name': name,
                'is_fulfill': fulfill,
                'recurse': recurse
            },
            soft=soft
        )

    def get_bundle_or_data(self, _id, fulfill=False, recurse=False):
        data = self.get_data(_id, soft=True)
        if not data:
            return self.get_bundle(_id, fulfill=fulfill, recurse=recurse) 
        return data 
