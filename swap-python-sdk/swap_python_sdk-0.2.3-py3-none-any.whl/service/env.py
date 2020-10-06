import os


def load_environmental_variables():
    os.environ['BUCKET'] = 'akerbp-stage-pilot-input'
    os.environ['DAS_URL'] = 'https://das.stage.swap.akerbp.com'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'auth/service_account_key.json'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['SERVICE_DISCOVERY_URL'] = 'https://service-discovery.stage.swap.akerbp.com'
    os.environ['UBL_URL'] = 'https://ubl.stage.swap.akerbp.com'

load_environmental_variables()
