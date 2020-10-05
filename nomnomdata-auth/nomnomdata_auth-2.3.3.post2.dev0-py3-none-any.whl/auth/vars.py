from pathlib import Path

CREDSTORE_PATH = Path.home() / Path(".nnd") / Path("credentials.json")
STAGING_COGNITO = {
    "userpool-id": "us-east-1_nV39p0EEf",
    "client-id": "7re90rqkr8htff06vstath1k92",
}
PROD_COGNITO = {
    "userpool-id": "us-east-1_2KqxYu7lz",
    "client-id": "43eemf1bian57itjki6qqeqrom",
}
COGNITO_NETLOC_MAPPING = {
    "user.api.nomnomdata.com": PROD_COGNITO,
    "staging.user.api.nomnomdata.com": STAGING_COGNITO,
    "user.api.nomitall.local": STAGING_COGNITO,
    "staging.web.nomnomdata.com": STAGING_COGNITO,
}

DEFAULT_PROFILE = "default"
