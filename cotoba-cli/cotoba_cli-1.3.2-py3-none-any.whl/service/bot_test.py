import click
import csv
import re
from cotoba_cli import platform


class InvalidTestError(click.ClickException):
    pass


def _is_compare_object(d):
    return type(d) is dict and '__compare_type' in d and '__compare_value' in d


def _extract_compare_type_value_pair(d):
    return (
        d['__compare_type'],
        d['__compare_value'],
    )


def compare_traverse(actual, expected):
    if _is_compare_object(expected):
        type_, value = _extract_compare_type_value_pair(expected)
        if type_ == 'regex' and type(actual) is str:
            return re.search(value, actual) is not None
        elif type_ == 'any':
            return compare_with_list(actual, value)
        elif type_ == 'equal':
            return actual == value
        else:
            return False

    elif type(expected) is str and expected.endswith('@regex'):
        value = expected.split('@')[0]
        return re.search(value, actual) is not None

    elif type(actual) is dict and type(expected) is dict:
        for key in (set(list(expected.keys())) | set(list(actual.keys()))):
            result = compare_traverse(actual[key], expected[key])
            if not result:
                return False
        return True

    else:
        return actual == expected


def compare_with_list(actual, expected_list):
    for expected in expected_list:
        if compare_traverse(actual, expected):
            return True
    return False


def ask_and_compare_tests(bot_id, api_key, tests, default_locale, show_progress=True):
    """
    todo: write tests format
    """
    results = []
    for test_number, test in enumerate(tests, 1):
        if 'request' not in test:
            raise click.ClickException('request field is required')
        if 'expected' not in test:
            raise click.ClickException('expected field is required')

        request = test['request']
        result = {}
        errors = []

        utterance = request.get('utterance')
        topic = request.get('topic')
        metadata = request.get('metadata')
        user_id = request.get('userId')
        locale = request.get('locale', default_locale)
        log_level = request.get('config', {}).get('logLevel')

        if utterance is None:
            errors.append('utterance is required.')

        if user_id is None:
            errors.append('userId is required.')

        if len(errors) > 0:
            if show_progress:
                click.secho(f'Error in test number {test_number}', fg='red', err=True)
                click.echo('-' * 16, err=True)
            result['errors'] = errors
            results.append(result)
            continue

        response_obj = platform.ask_bot(
            bot_id=bot_id,
            api_key=api_key,
            user_id=user_id,
            utterance=utterance,
            topic=topic,
            metadata=metadata,
            log_level=log_level,
            locale=locale)
        response = response_obj.get_response_body()
        result['utterance'] = utterance
        result['topic'] = response.get('topic')
        result['metadata'] = response.get('metadata')
        result['request_time'] = response_obj.get_request_time()
        result['response'] = response['response']

        expected = test['expected']
        result['expected'] = expected
        compare_keys = ['response', 'topic', 'metadata']
        compare_result = {}
        for key in compare_keys:
            if key not in expected:
                continue
            if expected[key] is list:
                compare_result[key] = compare_with_list(response.get(key), expected[key])
            else:
                compare_result[key] = compare_traverse(response.get(key), expected[key])
        result['compare_result'] = compare_result
        results.append(result)

        if show_progress:
            click.secho(f'utterance: {utterance}', fg='bright_magenta', err=True)
            click.secho(f'response: {response["response"]}', fg='bright_magenta', err=True)
            for key, result in compare_result.items():
                click.echo(f'compare result({key}): {_result_as_text(result)}', err=True)
            click.echo('-' * 16, err=True)

    return results


def output_rows_to_csv(rows_with_header, output_stream, write_header):
    if len(rows_with_header) == 0:
        return

    fieldnames = list(rows_with_header[0].keys())
    writer = csv.DictWriter(output_stream, fieldnames=fieldnames)
    if write_header:
        writer.writeheader()
    writer.writerows(rows_with_header)


def _result_as_text(result):
    if type(result) is bool:
        return 'OK' if result else 'NG'
    else:
        return None


def output_result_as_csv(compare_results, output_stream, write_header):
    rows_with_header = []
    for result in compare_results:
        if 'errors' in result:
            continue
        row = {
            'timestamp': result['request_time'],
            'utterance': result['utterance'],
            'response text': result['response'],
            'expected response text': result['expected'].get('response'),
            'response text result': _result_as_text(result['compare_result'].get('response')),
            'topic': result['topic'],
            'expected topic': result['expected'].get('topic'),
            'topic result': _result_as_text(result['compare_result'].get('topic')),
            'metadata': result['metadata'],
            'expected metadata': result['expected'].get('metadata'),
            'metadata result': _result_as_text(result['compare_result'].get('metadata'))
        }
        rows_with_header.append(row)

    output_rows_to_csv(rows_with_header, output_stream, write_header)
