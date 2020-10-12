#!/usr/bin/env python

import click

from libpipe import worker
from libpipe import __version__


t_file = click.Path(exists=True, dir_okay=False)


@click.group()
@click.version_option(__version__)
def main():
    ''' Nodes utilities ...'''


@main.command('run_all')
@click.argument('cmd_list', type=t_file)
@click.option('--nodes_string', '-n', help='Range of nodes to use', type=str, default='localhost')
@click.option('--max_concurrent', '-m', help='Maximum concurrent tasks on a node', type=int, default=5)
@click.option('--env_file', '-e', help='Environment source file', type=t_file)
@click.option('--dry_run', '-d', help='Dry run, only print commands', is_flag=True)
def run_all(cmd_list, nodes_string, max_concurrent, env_file, dry_run):
    ''' Run all command listed in the file CMD_LIST.'''
    pool = worker.get_worker_pool('Run All', nodes_string, max_concurrent=max_concurrent,
                                  env_file=env_file, dry_run=dry_run, debug=dry_run)

    for cmd in open(cmd_list).readlines():
        cmd = cmd.strip()
        pool.add(cmd)

    pool.execute()


@main.command('run_on_nodes')
@click.argument('cmd', nargs=-1)
@click.option('--nodes_string', '-n', help='Range of nodes to use', type=str, default='localhost')
@click.option('--env_file', '-e', help='Environment source file', type=t_file)
@click.option('--dry_run', '-d', help='Dry run, only print commands', is_flag=True)
def run_on_all_nodes(cmd, nodes_string, env_file, dry_run):
    ''' Run CMD on all nodes specified in argument.'''
    pool = worker.get_worker_pool('Run All', nodes_string, max_concurrent=2,
                                  env_file=env_file, dry_run=dry_run, debug=dry_run)

    cmd = ' '.join(cmd)

    for host in worker.get_hosts(nodes_string):
        pool.add(cmd, run_on_host=host)

    pool.execute()
