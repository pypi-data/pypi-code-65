import csv
import json
import logging
import os
import re

import click

from cotoba_cli import platform
from cotoba_cli import config
from cotoba_cli.service import bot_test
from cotoba_cli.util import validate_file_exists

logger = logging.getLogger(__name__)

REGEX_TALK_HISTORY = re.compile('--history-?(?P<type>[^ ]*)')
REGEX_TALK_HISTORY_NUMBER = re.compile('--history-?(?P<type>[^ ]*) '
                                       '(?P<history_size>[0-9]+)')
DEFAULT_HISTORY_SIZE = 10


@click.group(help='Talk API Interface and test scenario.')
def cli_test():
    pass


@cli_test.command(help='Repeat utterance and response.')
@click.option('--bot-id', 'bot_id', type=str, required=True, help='Bot ID.')
@click.option('--user-id', type=str, required=True, help='User ID.')
@click.option('--api-key', type=str, required=True, help='api-key.')
@click.option('--log-level',
              type=click.Choice(['none', 'error', 'warning', 'info', 'debug']),
              default='none',
              help='Detail level of information to be added to the log.')
@click.option('--directory', type=str, help='Output file directory.')
def talk(bot_id,
         user_id,
         api_key,
         log_level,
         directory):
    show_talk_mode_description()
    config_dict = config.load()['default']
    # 「exit」が入力されるまで発話 - 応答 を繰り返す
    while 1:
        input_utterance = input('> ')
        if input_utterance == '':
            continue

        if input_utterance == 'exit':
            click.echo('Exit talk mode.')
            break

        if '--history' in input_utterance:
            result = REGEX_TALK_HISTORY.match(input_utterance)
            history_type = None if result is None else result.group('type')
            result = REGEX_TALK_HISTORY_NUMBER.match(input_utterance)
            if result is not None and result.group('history_size').isnumeric():
                history_size = int(result.group('history_size'))
            else:
                history_size = DEFAULT_HISTORY_SIZE
            output_histories(
                history_type=history_type,
                history_size=history_size,
                bot_id=bot_id,
                api_key=api_key,
                user_id=user_id)
            continue
        is_show_topic = ' --show-topic' in input_utterance
        is_show_metadata = ' --show-meta' in input_utterance
        result = re.match(
            '(.*)( --show-topic| --show-metadata)(.*)',
            input_utterance)
        if result:
            # show-topic、show-meta両方指定を想定
            input_utterance = result.group(1) + result.group(3)
            result = re.match(
                '(.*)( --show-topic| --show-metadata)(.*)',
                input_utterance)
            if result:
                input_utterance = result.group(1) + result.group(3)

        topic = None
        if '--topic' in input_utterance:
            # オプションでトピック指定時はトピックを抽出
            result = re.match(
                '(.*)( --topic | --topic=)(.*)',
                input_utterance)
            input_utterance = result.group(1)
            topic = result.group(3)

        try:
            response_obj = platform.ask_bot(
                bot_id=bot_id,
                api_key=api_key,
                user_id=user_id,
                utterance=input_utterance,
                topic=topic,
                metadata=None,
                log_level=log_level,
                locale=config_dict.get('locale'))
        except Exception as e:
            click.secho(str(e.args), fg='red')
            return

        res = response_obj.get_response_body()
        if res == 'Internal Server Error':
            click.secho(res, fg='red')
            return

        if res.get('response'):
            click.secho(res.get('response'), fg='bright_magenta')

        if is_show_topic:
            response_topic = res.get('topic')
            response_topic = response_topic or ''
            click.echo('topic:' + click.style(
                response_topic, fg='bright_magenta'))
        if is_show_metadata:
            response_meta = res.get('metadata')
            text = response_meta or ''
            if isinstance(response_meta, dict):
                text = json.dumps(response_meta,
                                  ensure_ascii=False)
            click.echo('metadata:' + click.style(
                text, fg='bright_magenta'))
        if directory:
            csv_file_path = os.path.join(directory, bot_id + '_talk.csv')
            is_exists = os.path.exists(csv_file_path)
            with open(csv_file_path, 'a', newline='',
                      encoding='utf-8') as f:
                # ヘッダ部を設定
                fieldnames = [
                    'timestamp',
                    'topic(response)',
                    'utterance',
                    'response text',
                    'metadata'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not is_exists:
                    # ファイル非存在のみヘッダ部書き込み
                    writer.writeheader()
                row = {
                    "timestamp": response_obj.get_request_time(),
                    "topic(response)": res.get('topic'),
                    "utterance": input_utterance,
                    "response text": res.get('response'),
                    "metadata": res.get('metadata')
                }
                writer.writerow(row)


@cli_test.command(help='Compares response with expected and output results to file.')
@click.option('--bot-id', 'bot_id', type=str, required=True, help='Bot ID.')
@click.option('--api-key', type=str, required=True, help='api-key.')
@click.option('--file', 'test_file',
              callback=validate_file_exists, type=str, required=True, help='Test JSON file.')
@click.option('--ng-file/--no-ng-file', default=False)
@click.option('--directory', type=str, help='Output file directory.', default='./')
def compare(
        bot_id,
        api_key,
        test_file,
        ng_file,
        directory):
    config_dict = config.load()['default']
    with open(test_file, encoding='utf-8') as f:
        try:
            test_json = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f'{test_file} is invalid json file. {str(e)}')
    if 'test' not in test_json:
        raise click.ClickException('Test data is empty.')

    tests = test_json.get('test')
    results = bot_test.ask_and_compare_tests(
        bot_id=bot_id,
        api_key=api_key,
        tests=tests,
        default_locale=config_dict['locale'])

    if not os.path.exists(directory):
        os.mkdir(directory)
    csv_file_path = os.path.join(directory, bot_id + '_compare.csv')
    file_exists = os.path.exists(csv_file_path)
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as f:
        bot_test.output_result_as_csv(
            compare_results=results,
            output_stream=f,
            write_header=not file_exists)

    if ng_file:
        csv_ng_file_path = os.path.join(directory, bot_id + '_compare_ng.csv')
        ng_file_exists = os.path.exists(csv_ng_file_path)
        with open(csv_ng_file_path, 'a', newline='', encoding='utf-8') as f:
            ng_results = list(filter(lambda x: not all(x['compare_result'].values()), results))
            bot_test.output_result_as_csv(
                compare_results=ng_results,
                output_stream=f,
                write_header=not ng_file_exists)

    show_summary(results)


def show_summary(results):
    num_ok = 0
    num_ng = 0
    for result in results:
        for compare_result in result['compare_result'].values():
            if compare_result:
                num_ok += 1
            else:
                num_ng += 1

    click.echo(f'{num_ok} test(s) passed. {num_ng} test(s) failed.')


def output_histories(history_type,
                     history_size,
                     bot_id,
                     api_key,
                     user_id):
    histories = get_conversations_history(
        bot_id,
        api_key,
        user_id,
        history_size)
    if len(histories) == 0:
        click.echo('No histories.')
        return
    number_message = str(min(history_size, len(histories)))
    if history_type == 'in':
        history_message_type = 'utterance'
    elif history_type == 'out':
        history_message_type = 'response'
    else:
        history_message_type = 'utterance and response'
    message = f'Show the last ' \
        f'{number_message} {history_message_type} histories'
    click.echo(message)
    click.echo()
    for index, history in enumerate(histories):
        if history_type != 'out':
            click.secho(str(index + 1) + ':', nl=False)
            click.secho(history[0], fg='bright_blue')
        if history_type != 'in':
            click.secho(str(index + 1) + ':', nl=False)
            click.secho(history[1], fg='bright_green')


def get_conversations_history(bot_id,
                              api_key,
                              user_id,
                              history_size=None):
    debug_api_response = platform.debug_bot(bot_id=bot_id,
                                            api_key=api_key,
                                            user_id=user_id)
    response_json = debug_api_response.get_response_body()
    conversations = response_json.get('conversations')
    if conversations is None:
        return []
    questions = conversations.get('questions')
    sentences = [x['sentences'] for x in questions]
    histories = [(x['question'], x['response']) for y in sentences for x in y]
    if history_size:
        # Get the specified number of elements from the end.
        histories = histories[-history_size:]
    return histories


def show_talk_mode_description():
    click.secho('Start talk mode. '
                'If you enter "exit", exit talk mode.',
                fg='bright_cyan')
    echo_description('--topic',
                     'Topic ID.(e.g.:hello --topic greeting)')
    echo_description('--show-topic',
                     'Show response "topic".')
    echo_description('--show-metadata',
                     'Show response "metadata".')
    echo_description('--history-in',
                     'Show your input history. '
                     'By set parameter, specify number.')
    echo_description('--history-out',
                     'Show API response history. '
                     'By set parameter, specify number.')
    echo_description('--history',
                     'Show your input and API response history.')


def echo_description(command, help_text, columns=23):
    description = f'{command:<{columns}}' + help_text
    click.secho(description, fg='bright_cyan')
