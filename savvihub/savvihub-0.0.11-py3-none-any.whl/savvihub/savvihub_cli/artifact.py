import os

import typer
from requests_futures.sessions import FuturesSession
from savvihub.common.store import get_experiment, get_token

from savvihub.common.config import config
from savvihub.common.savvihub import SavviHubClient, SavviExperimentArtifact
from savvihub.common.utils import read_in_chunks

artifact_app = typer.Typer()


@artifact_app.callback()
def main():
    return


@artifact_app.command()
def sync(
    output_path_arg: str = typer.Argument("."),
):
    output_path = os.path.abspath(output_path_arg)

    files = []
    for root, _, files_ in os.walk(output_path):
        for name in files_:
            name = os.path.join(os.path.abspath(root), name)
            name = name[len(output_path)+1:] if name.startswith(output_path) else name
            files.append(name)

    typer.echo(f'Find {len(files)} files to upload.')

    def upload_file(path, pg):
        def fn(resp, **kwargs):
            resp.raise_for_status()
            print("Uploading ", path)
            progress.update(1)
        return fn

    with typer.progressbar(length=len(files)) as progress:
        token = get_token()
        experiment = get_experiment()

        session = FuturesSession(max_workers=config.parallel)
        client = SavviHubClient(token=token, session=session)

        # create files
        futures = [client.experiment_artifact_create(
            experiment.experiment_id,
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
                'response': upload_file(files[i], progress),
            },
        ) for i, resp in enumerate(resps)]
        [future.result() for future in futures]

    typer.echo(f'Uploaded {len(files)} files in {os.path.abspath(output_path)}')
