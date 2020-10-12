import os
from requests_futures.sessions import FuturesSession

import typer

from savvihub.savvihub_cli.config import config
from savvihub.savvihub_cli.constants import DEFAULT_CONFIG_PATH
from savvihub.savvihub_cli.savvihub import SavviHubClient, SavviDatasetFile
from savvihub.savvihub_cli.utils import calculate_crc32c, read_in_chunks, get_token_from_config

dataset_app = typer.Typer()


def parse_dataset_arg(dataset_arg):
    workspace, rest = dataset_arg.split("/")
    if ":" in rest:
        dataset, ref = rest.split(":")
    else:
        dataset = rest
        ref = "latest"
    return workspace, dataset, ref


@dataset_app.callback()
def main():
    return


@dataset_app.command()
def create():
    return


@dataset_app.command()
def push(
    dataset_arg: str = typer.Option(..., "-r"),
    root_path_arg: str = typer.Argument("."),
):
    root_path = os.path.abspath(root_path_arg)

    workspace, dataset, ref = parse_dataset_arg(dataset_arg)

    # download file list
    client = SavviHubClient(token=config.token)
    savvihub_files = client.dataset_file_list(workspace, dataset, ref=ref)

    # make hash map
    hash_map = dict()
    for file in savvihub_files:
        hash_map[file.path] = file.hash

    def path_and_hash(root, name):
        name = os.path.join(os.path.abspath(root), name)
        name = name[len(root_path)+1:] if name.startswith(root_path) else name
        return name, calculate_crc32c(name)

    files = []
    for root, _, files_ in os.walk(root_path):
        for name in files_:
            name, h = path_and_hash(root, name)
            if name in hash_map and hash_map[name] == h:
                continue
            files.append(name)

    typer.echo(f'Find {len(files)} files to upload.')

    with typer.progressbar(length=len(files)) as progress:
        session = FuturesSession(max_workers=config.parallel)
        client = SavviHubClient(token=config.token, session=session)

        # create files
        futures = [client.dataset_file_create(
            workspace, dataset, file_, False,
        ) for file_ in files]
        resps = [future.result() for future in futures]

        # upload files
        futures = [session.put(
            SavviDatasetFile(resp).upload_url,
            data=read_in_chunks(os.path.join(root_path, files[i])),
            headers={
                'content-type': 'application/octet-stream',
            },
            callback=lambda resp, **kwargs: resp.raise_for_status() or progress.update(1)
        ) for i, resp in enumerate(resps)]
        [future.result() for future in futures]

    typer.echo(f'Uploaded {len(files)} files in {os.path.abspath(root_path)}')


@dataset_app.command()
def pull(
    token: str = typer.Option(config.token, "-t", "--token"),
    parallel: int = typer.Option(config.parallel, "--parallel"),
    dataset_arg: str = typer.Argument(...),
    path_arg: str = typer.Argument("."),
):
    if token is None:
        token = get_token_from_config(DEFAULT_CONFIG_PATH)
    if parallel:
        config.parallel = parallel

    workspace, dataset, ref = parse_dataset_arg(dataset_arg)

    client = SavviHubClient(token=token)
    files = client.dataset_file_list(workspace, dataset, ref=ref, raise_error=True)

    def mkdir(file: SavviDatasetFile, pg):
        path = os.path.join(path_arg, file.path)
        if os.path.exists(path) and os.path.isdir(path):
            pg.update(1)
            return
        os.mkdir(path)
        pg.update(1)

    def download_file(file: SavviDatasetFile, pg):
        def fn(resp, **kwargs):
            path = os.path.join(path_arg, file.path)
            print("Downloading ", path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            pg.update(1)
        return fn

    with typer.progressbar(length=len(files)) as progress:
        session = FuturesSession(max_workers=config.parallel)
        [mkdir(file, progress) for file in files if file.is_dir]
        futures = [session.get(
            file.download_url,
            stream=True,
            hooks={
                'response': download_file(file, progress),
            },
        ) for file in files if not file.is_dir]
        [future.result() for future in futures]

    typer.echo(f'Downloaded {len(files)} files in {os.path.abspath(path_arg)}')


if __name__ == "__main__":
    dataset_app()