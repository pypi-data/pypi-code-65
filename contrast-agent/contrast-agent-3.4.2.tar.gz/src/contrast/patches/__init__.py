# -*- coding: utf-8 -*-
# Copyright © 2020 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import logging

logger = logging.getLogger("contrast")


from . import (
    cs_cstringio,
    cs_io,
    cs_logging,
    cs_re,
    threading_patch,
    exec_and_eval,
    lxml_patch,
    pycryptodome_patch,
    pyramid_patch,
)
from .databases import (
    mysql_connector_patch,
    pymysql_patch,
    psycopg2_patch,
    pycassa_patch,
    sqlalchemy_patch,
    sqlite3_patch,
)


COMMON_PATCH_MODULES = (
    cs_logging,
    threading_patch,
    # pycrypto_patch,
    pycryptodome_patch,
    # pycryptodomex_patch,
    sqlalchemy_patch,
    # our sqlite3_patch also contains the import hook for pysqlite2.dbapi2
    sqlite3_patch,
    mysql_connector_patch,
    pymysql_patch,
    psycopg2_patch,
    pycassa_patch,
)


ASSESS_PATCH_MODULES = (
    cs_cstringio,
    cs_io,
    cs_re,
    exec_and_eval,
    lxml_patch,
    pyramid_patch,
)


def register_module_patches(module, patch_group):
    logger.debug("registering %s patches for %s", patch_group, module.__name__)

    try:
        module.register_patches()
    except Exception:
        logger.exception("failed to register patches for %s", module.__name__)


def register_common_patches():
    for module in COMMON_PATCH_MODULES:
        register_module_patches(module, "common")


def register_assess_patches():
    for module in ASSESS_PATCH_MODULES:
        register_module_patches(module, "assess")
