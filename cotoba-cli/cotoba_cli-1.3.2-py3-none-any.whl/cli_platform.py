import logging

import click

from cotoba_cli import platform

from cotoba_cli import cli_test as test
from cotoba_cli import config
from cotoba_cli.util import validate_file_exists
from cotoba_cli.util import validate_end_date


logger = logging.getLogger(__name__)


class PlatformAliasedGroup(click.Group):
    COMMAND_ALIASES = {
        'list-bot': 'list-bots',
        'list-api-key': 'list-api-keys'
    }

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        exec_cmd_name = self.COMMAND_ALIASES.get(cmd_name)
        if exec_cmd_name is None:
            return None
        return click.Group.get_command(self, ctx, exec_cmd_name)


def global_platform_options(func):
    for option in reversed([
        click.option('--output-headers', is_flag=True,
                     help='Output response headers.')
    ]):
        func = option(func)
    return func


@click.group(cls=PlatformAliasedGroup, help='Operate bot features.')
def cli_platform():
    pass


@cli_platform.command(help='Print endpoint-url')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
def get_endpoint_url(bot_id):
    click.echo(platform.generate_ask_url(bot_id))


@cli_platform.command(help='Create a bot.')
@click.option('--file', 'file_path', type=str, required=True,
              callback=validate_file_exists, help='Path to zipped bot file.')
@click.option('--name', type=str, default=None)
@click.option('--message', type=str, default=None)
@click.option('--nlu-url', type=str, default=None)
@click.option('--nlu-api-key', type=str, default=None, help='Api key to access nlu url.')
@global_platform_options
def create_bot(file_path,
               name,
               message,
               nlu_url,
               nlu_api_key,
               output_headers):
    res = platform.create_bot(file_path,
                              name=name,
                              message=message,
                              nlu_url=nlu_url,
                              nlu_api_key=nlu_api_key)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Get a bot by bot id.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--output', 'zipfile_path', type=str,
              help='Download a scenario as zip file format.')
@global_platform_options
def get_bot(bot_id, zipfile_path, output_headers):
    res = platform.get_bot(bot_id,
                           zipfile_path)
    res.print(output_headers=output_headers)


@cli_platform.command(help='List bots.')
@global_platform_options
def list_bots(output_headers):
    res = platform.list_bots()
    res.print(output_headers=output_headers)


@cli_platform.command(help='Update bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--file', 'filepath', type=str,
              callback=validate_file_exists, help='File path to scenario zip file.')
@click.option('--name', type=str, default=None)
@click.option('--message', type=str, default=None)
@click.option('--nlu-url', type=str, default=None)
@click.option('--nlu-api-key', type=str, default=None,
              help='Api key to access nlu url.')
@global_platform_options
def update_bot(bot_id,
               filepath,
               name,
               message,
               nlu_url,
               nlu_api_key,
               output_headers):
    res = platform.update_bot(bot_id=bot_id,
                              filepath=filepath,
                              name=name,
                              message=message,
                              nlu_url=nlu_url,
                              nlu_api_key=nlu_api_key)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Delete bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@global_platform_options
def delete_bot(bot_id, output_headers):
    res = platform.delete_bot(bot_id)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Run bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--update', is_flag=True, help='Run running bot.')
@global_platform_options
def run_bot(bot_id, update, output_headers):
    res = platform.run_bot(bot_id, update)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Stop bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@global_platform_options
def stop_bot(bot_id, output_headers):
    res = platform.stop_bot(bot_id)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Ask bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--api-key', type=str, help='Api key.', required=True)
@click.option('--user-id', type=str, help='User id to keep conversation.',
              required=True)
@click.option('--utterance', type=str, help='Content of utterance.',
              required=True)
@click.option('--topic', type=str, help='Topic of utterance.',
              required=False)
@global_platform_options
def ask_bot(bot_id, api_key, user_id, utterance, topic, output_headers):
    res = platform.ask_bot(bot_id=bot_id,
                           api_key=api_key,
                           user_id=user_id,
                           utterance=utterance,
                           topic=topic,
                           locale=config.load()['default'].get('locale'))
    res.print(output_headers=output_headers)


@cli_platform.command(help='Debug bot.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--api-key', type=str, help='Api key.', required=True)
@click.option('--user-id', type=str, help='User id to keep conversation.')
@global_platform_options
def debug_bot(bot_id, api_key, user_id, output_headers):
    res = platform.debug_bot(bot_id=bot_id,
                             api_key=api_key,
                             user_id=user_id)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Create api-key.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--description', type=str, default=None,
              help='Describe the purpose of using api-key.')
@global_platform_options
def create_api_key(bot_id,
                   description,
                   output_headers):
    res = platform.create_api_key(bot_id=bot_id,
                                  expiration_days=None,
                                  max_api_calls=None,
                                  description=description)
    res.print(output_headers=output_headers)


@cli_platform.command(help='List api-keys.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@global_platform_options
def list_api_keys(bot_id, output_headers):
    res = platform.list_api_keys(bot_id=bot_id)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Get api-key.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--api-key-id', type=str, help='Api key id.', required=True)
@global_platform_options
def get_api_key(bot_id, api_key_id, output_headers):
    res = platform.get_api_key(bot_id=bot_id,
                               api_key=api_key_id)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Update api-key.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--api-key-id', type=str, help='Api key id.', required=True)
@click.option('--description',
              type=str,
              help='Describe the purpose of using api-key.',
              default=None)
@global_platform_options
def update_api_key(bot_id,
                   api_key_id,
                   description,
                   output_headers):
    res = platform.update_api_key(bot_id=bot_id,
                                  api_key=api_key_id,
                                  description=description)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Delete api-key.')
@click.option('--bot-id', type=str, help='Bot id.', required=True)
@click.option('--api-key-id', type=str, help='Api key id.', required=True)
@global_platform_options
def delete_api_key(bot_id, api_key_id, output_headers):
    res = platform.delete_api_key(bot_id=bot_id,
                                  api_key=api_key_id)
    res.print(output_headers=output_headers)


cli_platform.add_command(test.cli_test, 'test')


@cli_platform.command(help='Get bot logs.')
@click.option('--start-date', type=click.DateTime(['%Y-%m-%d']),
              help='Start date.')
@click.option('--end-date', type=click.DateTime(['%Y-%m-%d']),
              callback=validate_end_date, help='End date.')
@click.option('--limit', type=int, help='Maximum number of log.')
@click.option('--offset', type=int, default=0,
              help='Start index of log.')
@click.option('--bot-id', type=str, help='Bot id.')
@click.option('--api-key-id', type=str, help='Api key id.')
@global_platform_options
def get_bot_logs(start_date, end_date, limit, offset, bot_id,
                 api_key_id, output_headers):
    res = platform.get_bot_logs(start_date=start_date, end_date=end_date,
                                limit=limit, offset=offset,
                                bot_id=bot_id, api_key_id=api_key_id)
    res.print(output_headers=output_headers)


AGGREGATION_TYPES = ['hours', 'days', 'weeks', 'months', 'byHour']


@cli_platform.command(help='Get bot traffics.')
@click.option('--aggregation', type=click.Choice(AGGREGATION_TYPES),
              required=True, help='Aggregation type of traffics.')
@click.option('--start-date', type=click.DateTime(['%Y-%m-%d']),
              help='Start date.')
@click.option('--end-date', type=click.DateTime(['%Y-%m-%d']),
              callback=validate_end_date, help='End date.')
@click.option('--bot-id', type=str, help='Bot id.')
@click.option('--api-key-id', type=str, help='Api key id.')
@global_platform_options
def get_bot_traffics(aggregation, start_date, end_date, bot_id,
                     api_key_id, output_headers):
    res = platform.get_bot_traffics(aggregation,
                                    start_date=start_date, end_date=end_date,
                                    bot_id=bot_id, api_key_id=api_key_id)
    res.print(output_headers=output_headers)


@cli_platform.command(help='Get bot topics.')
@click.option('--aggregation', type=click.Choice(AGGREGATION_TYPES),
              required=True, help='Aggregation type of topics.')
@click.option('--start-date', type=click.DateTime(['%Y-%m-%d']),
              help='Start date.')
@click.option('--end-date', type=click.DateTime(['%Y-%m-%d']),
              callback=validate_end_date, help='End date.')
@click.option('--bot-id', type=str, help='Bot id.')
@click.option('--api-key-id', type=str, help='Api key id.')
@global_platform_options
def get_bot_topics(aggregation, start_date, end_date, bot_id,
                   api_key_id, output_headers):
    res = platform.get_bot_topics(aggregation,
                                  start_date=start_date, end_date=end_date,
                                  bot_id=bot_id, api_key_id=api_key_id)
    res.print(output_headers=output_headers)
