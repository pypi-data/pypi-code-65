import json
import os
import urllib.request

import click
import requests

HANDLE_URL_TEMPLATE = '{}/api/handles/{}'


@click.command()
@click.option('--handle-server', '-h', 'handle_server', required=False, default="http://handle.com",
              help='Location of the handle registry service')
@click.option('--cache', required=False, default=False, is_flag=True,
              help='If this flag is set the dataset is only loaded from CKAN '
                   'if it does not already exist in the specified target folder')
@click.option('--target', '-t', required=False, default='./',
              help='Target folder to which the dataset is going to be stored')
@click.option('--include-header', "include_header", required=False, is_flag=True,
              help='In case of csv export also include the headers to the resultset')
@click.option('--csv-delimiter', "delimiter", required=False, default=';',
              help='Specifies the delimiter in case the resultset is retrieved in csv format')
@click.option('--format', '-f', "format", required=False, default='json',
              help='specifies the format of the retrieved dataset [json|csv|xml]')
@click.argument('pid')
def retrieve_dataset(pid, handle_server, cache, target, format, include_header, delimiter):
    result = requests.get(HANDLE_URL_TEMPLATE.format(handle_server, pid))
    handle_values = json.loads(result.text)['values']

    api_url_entry = [value for value in handle_values if value['type'] == 'API_URL']
    api_url = api_url_entry[0]['data']['value']
    stream_url_entry = [value for value in handle_values if value['type'] == 'STREAM_URL']
    stream_url = stream_url_entry[0]['data']['value']

    response = requests.get(api_url)
    filename = response.json()['result']['meta'].get('citation_filename', pid.replace('/', '_'))
    filename = '{0}.{1}'.format(filename, format)

    if cache:
        if os.path.exists(os.path.join(target, filename)):
            click.echo('file already exists')
            return

    stream_url = '{0}?format={1}'.format(stream_url, format)
    stream_url += '&csvDelimiter={0}'.format(delimiter)

    if include_header:
        stream_url += '&includeHeader={0}'.format(include_header)
    else:
        stream_url += '&includeHeader=False'

    click.echo(stream_url)

    urllib.request.urlretrieve(stream_url, os.path.join(target, filename))


if __name__ == "__main__":
    retrieve_dataset()
