from setuptools import setup

setup(
    name='dc-jhub-jwtauthenticator',
    version='0.3-dev',
    description='JSONWebToken Authenticator for JupyterHub',
    tests_require = [
    'unittest2',
    ],
    test_suite = 'unittest2.collector',
    packages=['dc_jwtauthenticator'],
    install_requires=[
        'jupyterhub',
        'python-jose',
    ]
)