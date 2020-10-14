import os


def get_credentials_and_tenant_hostname(client):
    return {
        'User': os.environ["SAPBYDESIGN_%s_USERNAME" % client],
        'Password': os.environ["SAPBYDESIGN_%s_PASSWORD" % client],
    }, os.environ["SAPBYDESIGN_%s_TENANTHOSTNAME" % client]