
import distutils.version
import typing

import ldap

__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
]


# Princeton LDAP server
LDAP_HOSTNAME: str = "ldap.princeton.edu"

# LDAP URI with protocol scheme
LDAP_URI: str = "ldap://{hostname}".format(hostname=LDAP_HOSTNAME)

# Flag on whether using SSL/TLS
LDAP_URI_SECURE: bool = "ldaps://" in LDAP_URI

# Determine which version of the LDAP package
LDAP_24_API: bool = (distutils.version.LooseVersion(ldap.__version__) >=
                     distutils.version.LooseVersion("2.4"))

# Base domain name for Princeton University
LDAP_BASE_DN: str = "o=Princeton University,c=US"


