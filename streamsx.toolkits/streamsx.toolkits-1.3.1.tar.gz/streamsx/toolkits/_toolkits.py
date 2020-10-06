# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

# imports
import requests
import json
import re
from tempfile import gettempdir
import random
import wget
import string
import os
import tarfile
import shutil
import glob

from builtins import str
import jks
import OpenSSL
import sys
import warnings

# product toolkits
tkprodList = ['com.ibm.streamsx.avro',
              'com.ibm.streamsx.datetime',
              'com.ibm.streamsx.dps',
              'com.ibm.streamsx.elasticsearch',
              'com.ibm.streamsx.eventstore',
              'com.ibm.streamsx.hbase',
              'com.ibm.streamsx.hdfs',
              'com.ibm.streamsx.inet',
              'com.ibm.streamsx.inetserver',
              'com.ibm.streamsx.iot',
              'com.ibm.streamsx.jdbc',
              'com.ibm.streamsx.jms',
              'com.ibm.streamsx.json',
              'com.ibm.streamsx.kafka',
              'com.ibm.streamsx.mail',
              'com.ibm.streamsx.messagehub',
              'com.ibm.streamsx.mqtt',
              'com.ibm.streamsx.network',
              'com.ibm.streamsx.objectstorage',
              'com.ibm.streamsx.rabbitmq',
              'com.ibm.streamsx.sttgateway',
              'com.ibm.streamsx.topology'
            ]

pypackagelist = ['streamsx',
                 'streamsx.avro',
                 'streamsx.database',
                 'streamsx.elasticsearch',
                 'streamsx.endpoint',
                 'streamsx.eventstore',
                 'streamsx.eventstreams',
                 'streamsx.geospatial',
                 'streamsx.hbase', 
                 'streamsx.hdfs',
                 'streamsx.inet',
                 'streamsx.jms',
                 'streamsx.kafka',
                 'streamsx.mqtt',
                 'streamsx.objectstorage',
                 'streamsx.pmml',
                 'streamsx.standard',
                 'streamsx.sttgateway',
                 'streamsx.toolkits',
                 'streamsx.wml',
                ]



def _sorted_version(an_iterable):
    """ Sorts the given iterable in the way that is expected.

    Required arguments:
    an_iterable -- The iterable to be sorted.

    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(an_iterable, key = alphanum_key)


def _clean_dir(tmp_path, toolkit_dir, target_dir):
    for i in glob.glob(os.path.join(tmp_path, "*")):
        if os.path.isfile(i):
            os.remove(os.path.realpath(i))
        elif os.path.isdir(i):
            dirname = os.path.basename(i)
            if toolkit_dir != dirname:
                shutil.rmtree(os.path.realpath(i))
    shutil.move(os.path.join(tmp_path, toolkit_dir), target_dir)
    shutil.rmtree(tmp_path)


def _download_tk(url, name, toolkit_dir):
    """Downloads and unpacks the toolkit.
    
    Args:
        url(str): the download URL
        name(str): the subdirectory relative to the temporary directory (/tmp), where the toolkit is unpacked to
        toolkit_dir(str): the toolkit directory in the archive (where toolkit.xml is located)
    
    Returns:
        str: the absolute toolkit directory
    """
    rnd = ''.join(random.choice(string.digits) for _ in range(10))
    targetdir = os.path.join(gettempdir(), name)
    tmp_dir = targetdir + 'tmp'
    tmpfile = gettempdir() + '/' + 'toolkit-' + rnd + '.tgz'
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    if os.path.isdir(targetdir):
        shutil.rmtree(targetdir)
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    wget.download(url, tmpfile)
    #print (tmpfile + ": " + str(os.stat(tmpfile)))
    tar = tarfile.open(tmpfile, "r:gz")
    tar.extractall(path=tmp_dir)
    tar.close()
    # delete archive file
    os.remove(tmpfile)
    # clean-up all non toolkit dirs
    _clean_dir(tmp_dir, toolkit_dir, targetdir)
    # final toolkit location
    toolkit_path = targetdir
    # dump toolkit version
    tkfile = toolkit_path + '/toolkit.xml'
    if os.path.isfile(tkfile):
        f = open(tkfile, "r")
        for x in f:
            if 'toolkit name' in x:
                version_dump = re.sub(r' requiredProductVersion="[^ ]*"', '', x)
                print('\n'+version_dump)
                break
        f.close()
    return toolkit_path


def download_toolkit(toolkit_name, repository_name=None, url=None, target_dir=None):
    r"""Downloads the latest SPL toolkit from GitHub for the given toolkit name.

    Example for adding the com.ibm.streams.nlp toolkit with latest toolkit from GitHub::

        import streamsx.toolkits as tkutils
        # download toolkit from GitHub
        location = tkutils.download_toolkit('com.ibm.streamsx.nlp')
        # add toolkit to topology
        streamsx.spl.toolkit.add_toolkit(topo, location)

    Args:
        toolkit_name(str): the toolkit directory in the archive (where toolkit.xml is located), for example "com.ibm.streamsx.nlp"
        repository_name(str): name of the GitHub repository at "github.com/IBMStreams", for example "streamsx.nlp". Set this parameter if repository name is not part of toolkit name without "com.ibm.".
        url(str): the download URL, apply link to toolkit archive (\*.tgz) to be downloaded. 'https://github.com/IBMStreams/REPOSITORY-NAME/releases/latest' is used per default.
        target_dir(str): the directory where the toolkit is unpacked to. If a relative path is given,
            the target_dir is appended to the system temporary directory, for example to /tmp on Unix/Linux systems.
    
    Returns:
        str: the absolute path of the toolkit directory

    .. note:: This function requires an outgoing Internet connection
    """
    if repository_name is None:
        repo_name = toolkit_name[8::]
    else:
        repo_name = repository_name

    if target_dir is None:
        rnd = ''.join(random.choice(string.digits) for _ in range(10))
        target_dir = toolkit_name + '-' + rnd

    if url is None:
        # get latest toolkit
        r = requests.get('https://github.com/IBMStreams/'+repo_name+'/releases/latest')
        r.raise_for_status()
        if r.text is not None:
            s = re.search(r'/IBMStreams/'+repo_name+'/releases/download/.*tgz', r.text).group()
            url = 'https://github.com/' + s
    if url is not None:
        print('Download: ' + url)
        spl_toolkit = _download_tk(url, target_dir, toolkit_name)
    else:
        raise ValueError("Invalid URL")
    return spl_toolkit


def get_pypi_packages(package_name=None):
    """ Discover the latest Python packages available on pypi.org.
    
    Args:
        package_name(str): the name of the Python package to be searched for. If ``None`` is given,
        the function searches for all available streamsx Python packages.
        
    Returns:
        dict: A dictionary with mappings from Python package name to the package version

    .. note:: This function requires an outgoing Internet connection
    """
    pypi_packages = {}
    _pkg_list = pypackagelist if package_name is None else [package_name]

    for pkg_name in _pkg_list:
        r = requests.get('https://pypi.python.org/pypi/'+pkg_name+'/json')
        if r.status_code==200:
            data_json = r.json()
            releases = list(data_json["releases"].keys())
            final_releases = [] # remove alpha and beta releases
            for v in releases:
                if ((v.find('a') == -1) and (v.find('b') == -1)):
                    final_releases.append(v)
            latest_version = _sorted_version(final_releases)[-1]
            print(pkg_name + ' - ' + latest_version)
            pypi_packages[pkg_name]=latest_version
    return pypi_packages


def get_installed_packages():
    """ Discover installed `streamsx` python packages in your Python environment.

     Returns:
        dict: A dictionary with mappings from Python package name to the package version
   """
    installed_packages = {}
    for pkg_name in pypackagelist:
        try:
            import importlib
            i = importlib.import_module(pkg_name)
            if pkg_name is 'streamsx':
                import streamsx.topology.context
                print(pkg_name+' - ' + i.topology.context.__version__)
                installed_packages[pkg_name] = i.topology.context.__version__
            elif 'streamsx.standard' in pkg_name:
                import streamsx.standard._version
                print(pkg_name+' - ' + i._version.__version__)
                installed_packages[pkg_name] = i._version.__version__
            else:
                print(pkg_name+' - ' + i.__version__)
                installed_packages[pkg_name] = i.__version__
        except ImportError as error:
            print(pkg_name + ' NOT INSTALLED')
    return installed_packages


def get_build_service_toolkits(streams_cfg=None, verify=False):
    """ Discover toolkits on IBM Streams build service.
    
    Args:
        streams_cfg(dict): Service instance details of the IBM Streams instance. If value is None then the external build service endpoint is used.
        verify(bool): Set to True if SSL verification shall be enabled.
        
    Example, use the function in IBM Cloud Pak for Data with service instance details retrieved from icpd_util.get_service_details:: 

        from icpd_core import ipcd_util
        cfg = icpd_util.get_service_details(name='instanceName', instance_type='streams')
    
        import streamsx.toolkits as tkutils
        build_service_toolkits = tkutils.get_build_service_toolkits(cfg)
        print(build_service_toolkits)

    Returns:
        dict: A dictionary with mappings from toolkit name to the toolkit version
    """
    build_service_toolkits = {}
    from streamsx.build import BuildService
    from streamsx.topology import context

    if streams_cfg is None:
        buildService = BuildService.of_endpoint(verify=verify)
    else:
        streams_cfg[context.ConfigParams.SSL_VERIFY] = verify
        buildService = BuildService.of_service(streams_cfg)

    tks = buildService.get_toolkits()
    for x in tks:
        print (x.name + ' - ' + x.version)
        build_service_toolkits[x.name]=x.version
    return build_service_toolkits
        

def get_github_toolkits(toolkit_name=None):
    """ Discover the latest releases of product toolkits available on public GitHub.
    
    Args:
        toolkit_name(str): the name of the toolkit to be searched for. If ``None`` is given,
        the function searches for all product toolkits.
        
    Returns:
        dict: A dictionary with mappings from toolkit name to the toolkit version

    .. note:: This function requires an outgoing Internet connection
    """
    if toolkit_name is None:
        _tk_list = tkprodList
    else:
        _tk_list = [toolkit_name]
    github_toolkits = {}
    for tk_name in _tk_list:
        repo_name = tk_name[8::]
        r = requests.get('https://github.com/IBMStreams/'+repo_name+'/releases/latest')
        #print (r.url)
        if r.status_code==200:
            urlstr = r.url
            tk_version = None
            idx = urlstr.find('tag/v')
            if idx > -1:
                tk_version = urlstr[idx+5:]
            else:
                idx = urlstr.find('tag/')
                if idx > -1:
                    tk_version = urlstr[idx+4:]
            if tk_version is not None:
                print (tk_name + ' - ' + tk_version)
                github_toolkits[tk_name]=tk_version
    return github_toolkits


def _generate_password(len=16):
    """Generates a random password that consists of upper case letters, lower case letters and digits.
    
    Args:
        len(int) length of the generated password
        
    Returns:
        str: the passowrd
        
    .. versionadded:: 1.1
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(len))


def _try_read_from_file (potential_filename):
    """
    Reads data from a file or returns the data 'as is'.
    Args:
        potential_filename(str): the data, which can also be a filename.

    Returns:
        str: data read from file or the content of parameter 'potential_filename'

    """
    _data = potential_filename
    if os.path.exists (potential_filename) and os.path.isfile (potential_filename):
        with open(potential_filename, 'r') as data_file:
            _data = data_file.read()
#            print ("data read from file " + _data)
#    else:
#        print ("using data literally")
    return _data.strip()


def create_truststore(trusted_cert, store_filepath, store_passwd=None):
    """Creates a JKS type keystore from a single trusted certificate or a list of trusted certificates.
    A keystore with trusted certificates is therefore referred to as a *truststore*. 
    Truststores are typically used to store root certificates or self-signed certificates that servers present to clients.
    The aliases of the certificates in the keystore will be 'ca_cert-*i*', where *i* is a number starting at 0.

    Example::
    
        trusted_cert = \"\"\"
        -----BEGIN CERTIFICATE-----
        MIIDJzCCAg+gAwIBAgIJAJhu1pO2qbj7MA0GCSqGSIb3DQEBCwUAMCoxEzARBgNV
        BAoMCmlvLnN0cmltemkxEzARBgNVBAMMCmNsdXN0ZXItY2EwHhcNMTkwODE2MDc1
        ODI3WhcNMjAwODE1MDc1ODI3WjAqMRMwEQYDVQQKDAppby5zdHJpbXppMRMwEQYD
        VQQDDApjbHVzdGVyLWNhMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
        poC8jaqI9izS96CS39m4aOFruWDPxcrDsfU4gIbFveMHOV57F/LWkiC4GHWrcujj
        YHEKShMyP2rMfmQp148lxEZMc84zigB89ZUjWiFFR8PZBeX7syUmvTb/sEwWswOP
        epMUwqoNwDJ49HLQKbrSuZ+T4XymcPAmHU+Osm77hpJRGsloN1uVCBwzJJgxf9oz
        m0qLDMI4sw9GD3B8gjPZowZ70LtDnKkmG3hGXZwW1cvL2vuECdKWm77FUe+L2NVx
        c6cnZ5htNX0wjATf5hTN6uXsNUK/Xf6lKwcRgatYQVGT+kd+tDraHwhkID8cPyFi
        F+vbIhDzhKSBHGwYIGn+SwIDAQABo1AwTjAdBgNVHQ4EFgQUIYRTcQDd8rskiN2Q
        cV101xbmI9MwHwYDVR0jBBgwFoAUIYRTcQDd8rskiN2QcV101xbmI9MwDAYDVR0T
        BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAQtuxhqeT0z5fNB3Vs13TvVLfXPiG
        YSTwYvxfkrxGKtDiLjIZ6Q6LJjMcWLG4x3I0WmGgvytTs04S4B+1vp721jmqRKm9
        xCJ+Obi/eWmN4uu1rr0fR7fXr7wWLFBiDr8dZX3EnzjWeVWeNESoZTpaMKScuYTZ
        ocAT5iL3ZDUj/lwqJRptmzGFcdko+woFae68HRx1ygSgROls7bXy/CwgME0LFFQp
        B+2YAhUw1sPU410JUxU3/v6R5vJfI9imE75aha3U7UbeOX8+1+Cu3HOT1QMn80k2
        6LnZeMCCgCBp+Yz3YNeUMRejMU6x4WlhTPO7bBq3tKGgwCoyGIX25wMM1Q==
        -----END CERTIFICATE-----
        \"\"\"
        generated_truststore_password = create_truststore(trusted_cert, "/tmp/truststore.jks")
        
        # multiple certificates in existing files
        store_passwd = "Y3456tugzh"
        create_truststore(["/tmp/cert1.pem", "/tmp/cert2.pem"], "/tmp/truststore.jks", store_passwd)
    
    Args:
        trusted_cert(list|str): a list of filenames with trusted certificates in PEM format or the certificates literally
        store_filepath(str): the filename of the truststore file. The location must be writable. Intermediate directories are not created.
        store_passwd(str): the password for the keystore. When ``None``, a 16 characters password is generated.

    Returns:
        str: the generated or given password of the truststore

    **See also:** :py:func:`create_keystore`, :py:func:`extend_truststore`
    
    .. versionadded:: 1.1
    """
    if isinstance(trusted_cert, str):
        _cert_list = [trusted_cert]
    elif isinstance(trusted_cert, list):
        # must not be empty
        if trusted_cert:
            _cert_list = trusted_cert
        else:
            raise ValueError('trusted_cert must not be an empty list')
    else:
        raise TypeError('trusted_cert must be of str or list type')
    
    _passwd = store_passwd
    if _passwd is None:
        _passwd = _generate_password()
    _storeEntries = list()
    i = 0
    for _crt in _cert_list:
        _ca_cert_pem = _try_read_from_file(_crt)
        if not '---BEGIN' in _ca_cert_pem:
            warnings.warn('trusted certificate ' + _crt + ' does not look like in PEM format; no BEGIN anchor found', stacklevel=3)
        try:
            _cert = OpenSSL.crypto.load_certificate (OpenSSL.crypto.FILETYPE_PEM, bytes(_ca_cert_pem, 'utf-8'))
            _ca_cert_der = OpenSSL.crypto.dump_certificate (OpenSSL.crypto.FILETYPE_ASN1, _cert)
        except OpenSSL.crypto.Error as e:
            print('Error: Processing trusted certificate failed.', file=sys.stderr)
            raise
        _alias = 'ca_cert-' + str(i)
        _store_entry = jks.TrustedCertEntry.new (_alias, _ca_cert_der)
        _storeEntries.append(_store_entry)
        i = i + 1
    keystore = jks.KeyStore.new('jks', _storeEntries)
    keystore.save(store_filepath, _passwd)
    return _passwd


def extend_truststore(trusted_cert, store_filepath, store_passwd):
    """Extends an existing truststore by trusted certificate entries.

    Example::

        store_file = '/tmp/truststore.jks'
        store_passwd = create_truststore('/tmp/db.crt', store_filepath=store_file)
        # add two more certificates:
        extend_truststore(['/tmp/mqtt.crt', '/tmp/kafka.crt'],
                          store_filepath=store_file,
                          store_passwd=store_passwd)
    
    Args:
        trusted_cert(list|str): a list of filenames with trusted certificates in PEM format or the certificates literally
        store_filepath(str): the filename of the truststore file. The truststore must exist and be writable.
        store_passwd(str): the password for the given truststore.

    Returns:
        list: the aliases of the added entries

    **See also:** :py:func:`create_truststore`
    
    .. versionadded:: 1.2
    """
    if isinstance(trusted_cert, str):
        _cert_list = [trusted_cert]
    elif isinstance(trusted_cert, list):
        # must not be empty
        if trusted_cert:
            _cert_list = trusted_cert
        else:
            raise ValueError('trusted_cert must not be an empty list')
    else:
        raise TypeError('trusted_cert must be of str or list type')
    
    _keystore = jks.KeyStore.load(store_filepath, store_passwd, try_decrypt_keys=False)
    _entries = _keystore.entries
    _aliases = set(_entries.keys())
    _added_aliases = list()
    i = 0
    for _crt in _cert_list:
        _ca_cert_pem = _try_read_from_file(_crt)
        if not '---BEGIN' in _ca_cert_pem:
            warnings.warn('trusted certificate ' + _crt + ' does not look like in PEM format; no BEGIN anchor found', stacklevel=3)
        try:
            _cert = OpenSSL.crypto.load_certificate (OpenSSL.crypto.FILETYPE_PEM, bytes(_ca_cert_pem, 'utf-8'))
            _ca_cert_der = OpenSSL.crypto.dump_certificate (OpenSSL.crypto.FILETYPE_ASN1, _cert)
        except OpenSSL.crypto.Error as e:
            print('Error: Processing trusted certificate failed.', file=sys.stderr)
            raise
        
        _alias = 'ca_cert-' + str(i)
        while _alias in _aliases:
            i = i + 1
            _alias = 'ca_cert-' + str(i)
        _store_entry = jks.TrustedCertEntry.new (_alias, _ca_cert_der)
        _aliases.add(_alias)
        _entries[_alias] = _store_entry
        _added_aliases.append(_alias)
        i = i + 1
    _keystore.save(store_filepath, store_passwd)
    return _added_aliases


def create_keystore(client_cert, client_private_key, store_filepath, store_passwd=None):
    """Creates a JKS type keystore for a client certificate and its private RSA key.
    
    The aliases of the certificate in the keystore will be 'client_cert'.
    The private key will be encrypted with the store password.

    Example::
    
        client_cert = \"\"\"
        -----BEGIN CERTIFICATE-----
        MIICtjCCAZ4CCQCBrBBIDMiWTTANBgkqhkiG9w0BAQsFADAqMRMwEQYDVQQKDApp
        by5zdHJpbXppMRMwEQYDVQQDDApjbGllbnRzLWNhMB4XDTE5MDgxNjA5MzAzOVoX
        DTIwMDgwNjA5MzAzOVowEDEOMAwGA1UEAwwFcm9sZWYwggEiMA0GCSqGSIb3DQEB
        AQUAA4IBDwAwggEKAoIBAQC4rmdUhW0ZE0O7mwaYilIWb8Lqy/g4G7zYKa+5nVNI
        pM8Y9DLM6UmXFmO5SyiYWNzJCvbrj1u20deOrLetTpid6/LactoekVF6Gwkcy7uh
        FvkMvvzO00zU/7HGdzMRqwIWHZFVFQ7eNJcF5ITTPSyjfuXKCqVlTN70U6pVR1Kt
        jvh95U4qi6UxfrhfPSgX5rL1UgmMnYemeFWW9AmROk5FNOrXpiH9pRM9e034J/Lx
        X4fSArMc/HB2qmFkat5RSYNdYE47Upv/ufE0bl1CXvZ4hlKdQ2nyFV0ZkZ/IdtNV
        wXRczXmVKKEvCISTZWri1qFG2zs5ZibQXt2TWi/Hmb7rAgMBAAEwDQYJKoZIhvcN
        AQELBQADggEBABhDMkkXfGXagGY6EgZ4cev1h18jVm0uNknlUw6UXgLfoX7OBUmr
        yjfYWIqdNOewY3IZ1iTQHoEWXuFmuEUalb+CfYXdoZuHx/s211sLBy0S9pod3h+f
        VcwovrXqfE0V/Of5+3svE2p+O2N+UschjH/Ha9ljJ4CbVN0b/K8KkOt2dd6lMn2l
        jLyzjCBtnxBYnS1tbyILK6Mdb0Q6EeYBQw5K6x+f9gRvcyNpBcMMFZFk0n0Hr+zW
        4MuwSg7eM4OU1hExqUSILEfaVtsj4IgCimUN5RGEYBp8YFzT0GYnEm+c4iaEb4Uh
        1aDgpwpHly2t0dI7m3i2VYN4/UeRi2tXtS8=
        -----END CERTIFICATE-----
        \"\"\"
        
        private_key = \"\"\"
        -----BEGIN PRIVATE KEY-----
        MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC4rmdUhW0ZE0O7
        mwaYilIWb8Lqy/g4G7zYKa+5nVNIpM8Y9DLM6UmXFmO5SyiYWNzJCvbrj1u20deO
        rLetTpid6/LactoekVF6Gwkcy7uhFvkMvvzO00zU/7HGdzMRqwIWHZFVFQ7eNJcF
        5ITTPSyjfuXKCqVlTN70U6pVR1Ktjvh95U4qi6UxfrhfPSgX5rL1UgmMnYemeFWW
        9AmROk5FNOrXpiH9pRM9e034J/LxX4fSArMc/HB2qmFkat5RSYNdYE47Upv/ufE0
        bl1CXvZ4hlKdQ2nyFV0ZkZ/IdtNVwXRczXmVKKEvCISTZWri1qFG2zs5ZibQXt2T
        Wi/Hmb7rAgMBAAECggEBAJyes1zXprUcRFXm3AojTAhhEaGEB2a2B0oe2DsGtCmo
        M0XLWwWyVkl+oGX02mGRAvSwisUsl7AMd800prSgMgfDoPonatl/jeSK5wh3sxCj
        ZeSsV8OjKMZ+biqMzk+Ogj91JdpM+IXzfZxut0JZ3/Br3r6glrG5Jl94ULzvtqse
        YBXzi+9wbDjhzUrZea8GBSEgm4er8nGVlvl3cGA6B05KCkndSrpzJmD/1O1yHl2w
        jWcxnWbMjgJ+ZgTkWxNx1AACP1XnUubuHtH5X6CdyyexJVIcvSou29LE4AEgskzf
        N5f9g4WQqm/wqJouA6g2O2bYuH6RqPBR6LvRiWN+XCkCgYEA9W+xqD3EadT+9bkq
        SFkAHntFMnkmiu78azr5CSqXGZWiT12BloZg44Y4ouHkz0Q7UIOkuKnt8XUT+XTx
        cMJXdM/L8A7XadbLRGm+jQkPkamxzbhNha3RPqNcMmuSl+bus0/Y4CPlRzqmVFM2
        6i+7AJdSovt7ELPyB5VRoFTjqM8CgYEAwKFJ5C0DPbtm8lwf42Vg9lKReR2lhrdh
        70rIvuBwLpvmDEjT4E5XlCQZvmwCJhYQLeR7pdWTZUIUY3PRg6saUPt6mseQaY5G
        UMfd8eKNmYDq1dzw66L/rXVfLXL/U965mlchgrv1aYxFvS2oaXc06FGWf7HiX70r
        AYL3s4NsVyUCgYAntVFt4chkQvSY9sMzf0q4o8L3PoiQ08d85caiyAQ4PHBNHNi5
        bLZCOVXybE+jhOt/xDyjL8LyXLnFkzj4wEh7+p6JES2izwCF6gHNOZkOPQEqQlYw
        eYWv96gT9Dl8X/1gf1ucL9KJaqC8ZdYtn1lG6DSTb9JiSmqu9WaGZRWMGwKBgQCz
        Y4DUpbam/qbYfUKVGgw6WJpxGFLWKmFh31sjpw/R2A1c01W9Rjf5FcWDuEIoBdP7
        aRRdU5B4dBlYpLswy18um4OKMN8j7gM9p2PhpwIHOi94CtGyH5HLj8qbIMT27iwa
        t5nVjgT1zlQD4Uk9Lm5vC8wEDzypvBkYx0a2PmXeoQKBgQCdoz1xPj5Ltrocn992
        ci3mu3a5OxozeJVi36XSoWwr9HrK0arTaTEkbqcQxnjuCx/pIxM+FQQrVVjpAdop
        N1lLtfM0/X9cXohp2CwQGFldjOd7pF0t28ewN0wRij6oOdVa/u3EsVqijnhSEhOl
        YmR4uwOY4uG/ecALiF/2BBz5OA==
        -----END PRIVATE KEY-----
        \"\"\"
        key_store_password = create_keystore(client_cert, private_key, "/tmp/keystore.jks")
        
        # read key and certificate from existing files
        store_passwd = "Y3456tugzh"
        create_keystore("/tmp/client_cert.pem", "/tmp/client_priv_key.pem", "/tmp/keystore.jks", store_passwd)
    
    Args:
        client_cert(str): the filename with a client certificate in PEM format or the certificate itself
        client_private_key(str): the filename with a private key in PEM format or the private key itself
        store_filepath(str): the filename of the keystore file. The location must be writable. Intermediate directories are not created.
        store_passwd(str): the password for the private key and the keystore. When ``None``, a 16 characters password is generated.

    Returns:
        str: the generated or given password of the keystore and the private key
        
    **See also:** :py:func:`create_truststore`, :py:func:`extend_keystore`
    
    .. versionadded:: 1.1
    """
    _client_cert_pem = _try_read_from_file(client_cert)
    if not '---BEGIN' in _client_cert_pem:
        warnings.warn('client certificate ' + client_cert + ' does not look like in PEM format; no BEGIN anchor found', stacklevel=3)
    _client_key_pem = _try_read_from_file(client_private_key)
    if not '---BEGIN' in _client_key_pem:
        warnings.warn('client private key ' + client_private_key + ' does not look like in PEM format; no BEGIN anchor found', stacklevel=3)

    _passwd = store_passwd
    if _passwd is None:
        _passwd = _generate_password()
    try:
        _cert = OpenSSL.crypto.load_certificate (OpenSSL.crypto.FILETYPE_PEM, bytes(_client_cert_pem, 'utf-8'))
        _client_cer_der = OpenSSL.crypto.dump_certificate (OpenSSL.crypto.FILETYPE_ASN1, _cert)
    except OpenSSL.crypto.Error as e:
        print('Error: Processing client certificate failed.', file=sys.stderr)
        raise
    try:
        _key = OpenSSL.crypto.load_privatekey (OpenSSL.crypto.FILETYPE_PEM, bytes(_client_key_pem, 'utf-8'))
        _client_key_der = OpenSSL.crypto.dump_privatekey (OpenSSL.crypto.FILETYPE_ASN1, _key)
    except OpenSSL.crypto.Error as e:
        print('Error: Processing client private key failed.', file=sys.stderr)
        raise

    try:
        privateKeyEntry = jks.PrivateKeyEntry.new("client_cert", [_client_cer_der], _client_key_der, 'rsa_raw')
    except Exception:
        print('Error: Processing client private key failed. Not RSA format?', file=sys.stderr)
        raise
    
    if privateKeyEntry.is_decrypted():
        privateKeyEntry.encrypt(_passwd)
    keystore = jks.KeyStore.new('jks', [privateKeyEntry])
    keystore.save(store_filepath, _passwd)
    return _passwd


def extend_keystore(client_cert, client_private_key, store_filepath, store_passwd):
    """Extends a JKS type keystore with a client certificate and its private RSA key.
    
    The alias of the certificate in the keystore will be client_cert-*<n>*.
    The private key will be encrypted with the store password.
    
    Example::
    
        store_file = '/tmp/keystore.jks'
        store_passwd = create_keystore(client_cert='/tmp/db_client.crt',
                                       client_private_key='/tmp/db_client.key',
                                       store_filepath=store_file)
        extend_keystore(client_cert='/tmp/mqtt_client.crt',
                        client_private_key='/tmp/mqtt_client.key',
                        store_filepath=store_file,
                        store_passwd=store_passwd)
    
    Args:
        client_cert(str): the filename with a client certificate in PEM format or the certificate itself
        client_private_key(str): the filename with a private key in PEM format or the private key itself
        store_filepath(str): the filename of the keystore file. The file must exist and be writable.
        store_passwd(str): the password for the keystore. It is also used to encrypt the given private key.
        
    Returns:
        list: the aliases of the added entries (currently a list with one element)
        
    **See also:** :py:func:`create_keystore`
    
    .. versionadded:: 1.2
    """
    _client_cert_pem = _try_read_from_file(client_cert)
    if not '---BEGIN' in _client_cert_pem:
        warnings.warn('client certificate ' + client_cert + ' does not look like in PEM format; no BEGIN anchor found', stacklevel=3)
    _client_key_pem = _try_read_from_file(client_private_key)
    if not '---BEGIN' in _client_key_pem:
        warnings.warn('client private key ' + client_private_key + ' does not look like in PEM format; no BEGIN anchor found', stacklevel=3)
    _keystore = jks.KeyStore.load(store_filepath, store_passwd, try_decrypt_keys=False)
    _entries = _keystore.entries
    _aliases = set(_entries.keys())

    try:
        _cert = OpenSSL.crypto.load_certificate (OpenSSL.crypto.FILETYPE_PEM, bytes(_client_cert_pem, 'utf-8'))
        _client_cer_der = OpenSSL.crypto.dump_certificate (OpenSSL.crypto.FILETYPE_ASN1, _cert)
    except OpenSSL.crypto.Error as e:
        print('Error: Processing client certificate failed.', file=sys.stderr)
        raise
    try:
        _key = OpenSSL.crypto.load_privatekey (OpenSSL.crypto.FILETYPE_PEM, bytes(_client_key_pem, 'utf-8'))
        _client_key_der = OpenSSL.crypto.dump_privatekey (OpenSSL.crypto.FILETYPE_ASN1, _key)
    except OpenSSL.crypto.Error as e:
        print('Error: Processing client private key failed.', file=sys.stderr)
        raise
    i = 0
    _alias = 'client_cert-' + str(i)
    while _alias in _aliases:
        i = i + 1
        _alias = 'client_cert-' + str(i)

    try:
        privateKeyEntry = jks.PrivateKeyEntry.new(_alias, [_client_cer_der], _client_key_der, 'rsa_raw')
    except Exception:
        print('Error: Processing client private key failed. Not RSA format?', file=sys.stderr)
        raise
    
    if privateKeyEntry.is_decrypted():
        privateKeyEntry.encrypt(store_passwd)
    
    _entries[_alias] = privateKeyEntry
    _keystore.save(store_filepath, store_passwd)
    return [_alias]
