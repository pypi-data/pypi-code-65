# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
# to use this:
#   python -m qblocal_backup qbittorrent/conf dest_location
# ----------

from typing import *
import os
import sys
import traceback
import logging
from datetime import datetime

from . import backup_qbittorrent

def get_timestr():
    dtstr = datetime.now().isoformat()[:19]
    return dtstr.replace(':', '-')

def find_backups(basedir: str, prefix: str):
    '''
    find backups in dir, order by new to old, return the list of fullpath.
    '''

    zips = [f for f in os.listdir(basedir) if os.path.splitext(f)[1] == '.zip' and f.startswith(prefix)]
    if zips:
        zips.sort(reverse=True)
    return [os.path.join(basedir, n) for n in zips]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    logger = logging.getLogger('qblocal.backup')
    logging.basicConfig(level=logging.WARNING, format='%(message)s')
    logger.setLevel(logging.INFO)

    if sys.getdefaultencoding() != 'utf-8':
        logger.warning(f'encoding is {sys.getdefaultencoding()}, which may cause errors.')

    args = argv[1:]
    if len(args) != 2:
        return exit('module qblocal_backup required 2 parameters: <QBITTORRENT_CONF> <DEST_LOCATION>')
    conf_location, dest_dir = args

    try:
        if not os.path.isdir(conf_location):
            return exit(f'{conf_location} is not a dir.')
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        prefix = 'qbittorrent-'
        destzip_path = os.path.join(dest_dir, f'{prefix}{get_timestr()}.zip')

        exists = find_backups(dest_dir, prefix)
        backup_qbittorrent(
            conf_location, destzip_path,
            last_backupzip_path=next(iter(exists), None),
            logger=logger)

        # cleanup
        exists = find_backups(dest_dir, prefix)
        while len(exists) > 5:
            os.unlink(exists.pop())

    except Exception: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()

