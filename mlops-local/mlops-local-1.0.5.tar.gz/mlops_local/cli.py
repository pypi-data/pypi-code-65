import click
import docker
import os
import json
import subprocess

HOME = os.environ['HOME']


@click.group()
def cli():
    pass


@click.command()
def start():
    print("Starting MLOps...")
    client = docker.from_env()
    if len(client.images.list(name='mlopscloud/local')) == 0:
        print("MLOps local container not found, pulling.")
        client.images.pull(repository='mlopscloud/local', tag='latest')
        print('Done.')
    client.containers.run(
        image='mlopscloud/local:latest',
        environment=["MLOPS_LOCAL=True"],
        name='mlopslocal',
        volumes={
            f"{HOME}/mlops": {'bind': "/mlops/run", 'mode': 'rw'}
        },
        detach=True,
        ports={'5000/tcp': 5000}
    )
    print('Ready to serve! Head over to the console to start testing.')


@click.command()
def stop():
    print("Stopping MLOps...")
    client = docker.from_env()
    try:
        mlops_local = client.containers.get(container_id='mlopslocal')
    except docker.errors.ImageNotFound:
        print('Container not running.')
        return
    print("SIGTERM sent.")
    mlops_local.kill()
    mlops_local.remove()
    print("MLOps local has been stopped.")


cli.add_command(start)
cli.add_command(stop)

'''
def main():
    mlops.cli()
'''
