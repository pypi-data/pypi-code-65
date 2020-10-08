import os

import typer
from requests_futures.sessions import FuturesSession

from savvihub.savvihub_cli.config import config
from savvihub.savvihub_cli.savvihub import SavviHubClient, SavviExperimentArtifact
from savvihub.savvihub_cli.utils import read_in_chunks

artifact_app = typer.Typer()


@artifact_app.callback()
def main():
    return


@artifact_app.command()
def sync(
    token: str = typer.Option(config.token, "--token"),
    experiment_id: str = typer.Option(..., "-e"),
    output_path_arg: str = typer.Argument("."),
):
    output_path = os.path.abspath(output_path_arg)

    files = []
    for root, _, files_ in os.walk(output_path):
        for name in files_:
            name = os.path.join(os.path.abspath(root), name)
            name = name[len(output_path)+1:] if name.startswith(output_path) else name
            files.append(name)

    with typer.progressbar(length=len(files)) as progress:
        session = FuturesSession(max_workers=config.parallel)
        client = SavviHubClient(token=token, session=session)

        # create files
        futures = [client.experiment_artifact_create(
            experiment_id,
            file_,
            hooks={
                'response': lambda resp, **kwargs: resp.raise_for_status()
            },
        ) for file_ in files]
        resps = [future.result() for future in futures]

        # upload files
        futures = [session.put(
            SavviExperimentArtifact(resp.json()).upload_url,
            data=read_in_chunks(os.path.join(output_path, files[i])),
            headers={
                'content-type': 'application/octet-stream',
            },
            hooks={
                'response': lambda resp, **kwargs: resp.raise_for_status() or progress.update(1),
            },
        ) for i, resp in enumerate(resps)]
        [future.result() for future in futures]

    typer.echo(f'Uploaded {len(files)} files in {os.path.abspath(output_path)}')
