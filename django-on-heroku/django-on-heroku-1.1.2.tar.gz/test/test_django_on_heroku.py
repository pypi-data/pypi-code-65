import os
import importlib

import testproject.settings as config


def test_geodjango_databases():
    # Mock geodjango environment.
    os.environ['BUILD_WITH_GEO_LIBRARIES'] = '1'
    os.environ['DATABASE_URL'] = 'postgres://fake:fake@fake.com/fake'
    importlib.reload(config)

    assert 'django.contrib.gis' in config.DATABASES['default']['ENGINE']

    # Cleanup environment for further tests.
    del os.environ['BUILD_WITH_GEO_LIBRARIES']


def test_databases():
    os.environ['DATABASE_URL'] = 'postgres://fake:fake@fake.com/fake'
    importlib.reload(config)
    assert 'postgres' in config.DATABASES['default']['ENGINE']


def test_max_conn_age():
    os.environ['CONN_MAX_AGE'] = '700'
    os.environ['DATABASE_URL'] = 'postgres://fake:fake@fake.com/fake'
    importlib.reload(config)

    assert config.DATABASES['default']['CONN_MAX_AGE'] == 700

    del os.environ['CONN_MAX_AGE']


def test_test_runner():
    # Mock CI environment.
    os.environ['CI'] = '1'
    importlib.reload(config)

    assert 'heroku' in config.TEST_RUNNER.lower()

    # Cleanup environment for further tests.
    del os.environ['CI']


def test_staticfiles():
    importlib.reload(config)
    assert config.STATIC_URL == '/static/'
    assert 'whitenoise' in config.MIDDLEWARE[1].lower()


def test_allowed_hosts():
    importlib.reload(config)
    assert config.ALLOWED_HOSTS == ['*']


def test_logging():
    importlib.reload(config)
    assert 'console' in config.LOGGING['handlers']


def test_secret_key():
    os.environ['SECRET_KEY'] = 'SECRET'

    importlib.reload(config)
    assert config.SECRET_KEY == 'SECRET'
