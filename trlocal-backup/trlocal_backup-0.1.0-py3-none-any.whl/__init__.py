# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
from typing import Dict, List
from zipfile import ZipFile
from logging import Logger

def backup_transmission(trconfig_dir: str, destzip_path: str,
                        last_backupzip_path: str=None, logger: Logger=None):

    '''
    - `trconfig_dir` - the transmission config dir, which should contains a `torrents` dir.
    - `destzip_path` - the dest zip file path to save the backup files.
    - `last_backupzip_path` - the last backuped zip file to compare if provided.
    '''

    torrents_dir = os.path.join(trconfig_dir, 'torrents')
    if not os.path.isdir(torrents_dir):
        logger.error(f'{torrents_dir} is not a dir.')
        return

    files_to_backup: Dict[str, str] = {}
    for name in os.listdir(torrents_dir):
        if os.path.splitext(name)[1] == '.torrent':
            arc_name = 'torrents/' + name
            files_to_backup[arc_name] = os.path.join(torrents_dir, name)

    # load exists backups
    if last_backupzip_path:
        with ZipFile(last_backupzip_path, 'r') as last_backup_zip:
            last_backup_torrents = set(last_backup_zip.namelist())
    else:
        last_backup_torrents = set()

    if last_backup_torrents == set(files_to_backup):
        logger.info('nothing changed after last backup.')
        return

    zipsafe = False
    try:
        with ZipFile(destzip_path, 'w') as backup_file:
            for arc_name in sorted(files_to_backup):
                try:
                    backup_file.write(files_to_backup[arc_name], arc_name)
                except:
                    logger.error('error when backuping {}'.format(arc_name), exc_info=True)
                    raise
        zipsafe = True
    finally:
        if not zipsafe and os.path.exists(destzip_path):
            try:
                os.unlink(destzip_path)
            except:
                pass
