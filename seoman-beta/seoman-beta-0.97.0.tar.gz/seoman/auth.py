import collections.abc
import json

from apiclient import discovery  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore

from pathlib import Path
from typing import Dict, Any, Optional, Union, List, IO

from .service import SearchAnalytics
from .exceptions import BrokenFileError


def authenticate(
    client_config: Union[str, Path] = None,
    credentials: Union[Any, Dict[str, Dict[str, str]]] = None,
    serialize: Union[str, Path] = None,
    flow: str = "web",
) -> discovery.Resource:

    if not credentials:

        if isinstance(client_config, collections.abc.Mapping):

            auth_flow = InstalledAppFlow.from_client_config(
                client_config=client_config,
                scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
            )

        elif isinstance(client_config, str):

            auth_flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=client_config,
                scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
            )

        else:
            raise BrokenFileError("Client secrets must be a mapping or path to file")

        if flow == "web":
            auth_flow.run_local_server()
        elif flow == "console":
            auth_flow.run_console()
        else:
            raise ValueError("Authentication flow '{}' not supported".format(flow))

        credentials = auth_flow.credentials

    else:

        if isinstance(credentials, str):
            try:
                with open(credentials, "r") as f:
                    credentials = json.load(f)
            except FileNotFoundError:
                print(
                    "\nAuthentication failed ❌\nReason: credentials.json not found in your current directory."
                )
                exit()

        credentials = Credentials(
            token=credentials["token"],
            refresh_token=credentials["refresh_token"],
            id_token=credentials["id_token"],
            token_uri=credentials["token_uri"],
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            scopes=credentials["scopes"],
        )

    service = discovery.build(
        serviceName="webmasters",
        version="v3",
        credentials=credentials,
        cache_discovery=False,
    )

    if serialize:

        if isinstance(serialize, str):

            serialized = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "id_token": credentials.id_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }

            with open(serialize, "w") as f:
                json.dump(serialized, f, indent=4)

        else:
            raise TypeError("`serialize` must be a path.")

    return SearchAnalytics(service, credentials)


def load_service(
    credentials: Optional[str] = f"{Path.cwd()}/credentials.json",
) -> SearchAnalytics:

    service = authenticate(credentials=credentials)
    return service


def get_authenticated(
    client_config: Optional[str] = f"{Path.cwd()}/client_secrets.json",
    serialize: Optional[str] = f"{Path.cwd()}/credentials.json",
) -> SearchAnalytics:

    service = authenticate(client_config=client_config, serialize=serialize)
    return service
