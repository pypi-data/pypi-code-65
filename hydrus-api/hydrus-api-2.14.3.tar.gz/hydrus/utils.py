import collections
import typing as T

from . import Client, Permission, DEFAULT_API_URL, HYDRUS_METADATA_ENCODING


def verify_permissions(client: Client, permissions: T.List[Permission], exact: bool = False) -> bool:
    granted_permissions = set(client.verify_access_key()["basic_permissions"])
    return granted_permissions == set(permissions) if exact else granted_permissions.issuperset(permissions)


def cli_request_api_key(
    name: str,
    permissions: T.List[Permission],
    verify: bool = True,
    exact: bool = False,
    api_url: str = DEFAULT_API_URL,
) -> str:
    while True:
        input(
            'Navigate to "services->review services->local->client api" in the Hydrus client and click "add->from api '
            'request". Then press enter to continue...'
        )
        access_key = Client(api_url=api_url).request_new_permissions(name, permissions)
        input("Press OK and then apply in the Hydrus client dialog. Then press enter to continue...")

        client = Client(access_key, api_url)
        if verify and not verify_permissions(client, permissions, exact):
            granted_permissions = client.verify_access_key()["basic_permissions"]
            print(
                "The granted permissions ({}) differ from the requested permissions ({}), please grant all requested "
                "permissions.".format(granted_permissions, permissions)
            )
            continue

        return access_key


def parse_hydrus_metadata(text: str) -> T.DefaultDict[T.Optional[str], T.Set[str]]:
    namespaces = collections.defaultdict(set)
    for line in (line.strip() for line in text.splitlines()):
        if not line:
            continue

        parts = line.split(":", 1)
        if len(parts) == 1:
            namespace, tag = None, line
        else:
            namespace, tag = parts
        namespaces[namespace].add(tag)

    return namespaces


def parse_hydrus_metadata_file(path_or_file: T.Union[str, T.TextIO]) -> T.DefaultDict[T.Optional[str], T.Set[str]]:
    if isinstance(path_or_file, str):
        with open(path_or_file, encoding=HYDRUS_METADATA_ENCODING) as file:
            return parse_hydrus_metadata(file.read())

    return parse_hydrus_metadata(path_or_file.read())


# Useful for splitting up requests to file_metadata()
def yield_chunks(sequence: T.Sequence, chunk_size: int, offset: int = 0) -> T.Generator[T.Any, None, None]:
    while offset < len(sequence):
        yield sequence[offset : offset + chunk_size]
        offset += chunk_size
