from flask import Blueprint, Response, request, stream_with_context

import cirrocumulus.data_processing as data_processing
from .auth_api import AuthAPI
from .database_api import DatabaseAPI
from .dataset_api import DatasetAPI
from .invalid_usage import InvalidUsage
from .util import *


blueprint = Blueprint('blueprint', __name__)

dataset_api = DatasetAPI()

auth_api = AuthAPI()
database_api = DatabaseAPI()


@blueprint.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    return Response(error.message, error.status_code)


@blueprint.route('/server', methods=['GET'])
def handle_server():
    # no login required
    server = database_api.server()
    server['clientId'] = auth_api.client_id
    return to_json(server)


@blueprint.route('/filters', methods=['GET'])
def handle_dataset_filters():
    """List filters available for a dataset.
    """
    email = auth_api.auth()['email']
    dataset_id = request.args.get('id', '')

    if dataset_id == '':
        return 'Please provide an id', 400

    dataset_filters = database_api.dataset_filters(email, dataset_id)
    # {'id': result.id, 'name': result['name']}
    return to_json(dataset_filters)


@blueprint.route('/export_filters', methods=['GET'])
def handle_export_dataset_filters():
    """Download filters in a csv file for a dataset.
    """
    email = auth_api.auth()['email']
    dataset_id = request.args.get('id', '')

    if dataset_id == '':
        return 'Please provide an id', 400

    dataset_filters = database_api.dataset_filters(email, dataset_id)
    dataset = database_api.get_dataset(email, dataset_id)
    text = data_processing.handle_export_dataset_filters(dataset_api, dataset, dataset_filters)
    return Response(text, mimetype='text/plain')


@blueprint.route('/category_name', methods=['GET', 'PUT'])
def handle_category_name():
    """CRUD for category name.
    """

    email = auth_api.auth()['email']
    if request.method == 'GET':
        dataset_id = request.args.get('id', '')
        if dataset_id == '':
            return 'Please provide an id', 400
        return to_json(database_api.category_names(email, dataset_id))
    content = request.get_json(force=True, cache=False)
    category = content.get('c')
    original_name = content.get('o')
    new_name = content.get('n')
    dataset_id = content.get('id')
    if request.method == 'PUT':
        database_api.upsert_category_name(
            email=email,
            category=category,
            dataset_id=dataset_id,
            original_name=original_name,
            new_name=new_name)
        return '', 200


@blueprint.route('/filter', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_dataset_filter():
    """CRUD for a dataset filter.
    """

    email = auth_api.auth()['email']
    if request.method == 'GET':
        filter_id = request.args.get('id', '')
        dataset_id = request.args.get('ds_id', '')
        if filter_id == '' or dataset_id == '':
            return 'Please provide an id', 400
        return to_json(database_api.get_dataset_filter(email, dataset_id=dataset_id, filter_id=filter_id))
    content = request.get_json(force=True, cache=False)
    filter_id = content.get('id')
    dataset_id = content.get('ds_id')
    # POST=new, PUT=update , DELETE=delete, GET=get
    if request.method == 'PUT' or request.method == 'POST':
        if request.method == 'PUT' and filter_id is None:
            return 'Please supply an id', 400
        if request.method == 'POST' and dataset_id is None:
            return 'Please supply a ds_id', 400
        dataset_filter = content.get('value')
        filter_name = content.get('name')
        filter_notes = content.get('notes')
        filter_id = database_api.upsert_dataset_filter(
            email=email,
            dataset_id=dataset_id,
            filter_id=filter_id if request.method == 'PUT' else None,
            dataset_filter=dataset_filter,
            filter_name=filter_name,
            filter_notes=filter_notes)
        return to_json({'id': filter_id})
    elif request.method == 'DELETE':
        database_api.delete_dataset_filter(email, dataset_id=dataset_id, filter_id=filter_id)
        return to_json('', 204)


@blueprint.route('/schema', methods=['GET'])
def handle_schema():
    """Get dataset schema.
    """
    email = auth_api.auth()['email']
    dataset_id = request.args.get('id', '')
    dataset = database_api.get_dataset(email, dataset_id)
    schema = dataset_api.schema(dataset)
    return to_json(schema)


@blueprint.route('/file', methods=['GET'])
def handle_file():
    email = auth_api.auth()['email']
    dataset_id = request.args.get('id', '')
    dataset = database_api.get_dataset(email, dataset_id)
    file = request.args.get('file')
    url = dataset['url']
    import os
    import mimetypes
    file_path = os.path.join(os.path.dirname(url), os.path.abspath(file))
    mimetype = mimetypes.guess_type(file_path)
    # with dataset_api.fs_adapter.get_fs(file_path).open(file_path) as f:
    #     bytes = f.read()
    # return Response(bytes, mimetype=mimetype[0])
    chunk_size = 4096
    f = dataset_api.fs_adapter.get_fs(file_path).open(file_path)

    def generate():
        while True:
            chunk = f.read(chunk_size)
            if len(chunk) <= 0:
                f.close()
                break
            yield chunk

    response = Response(stream_with_context(generate()), mimetype=mimetype[0])
    return response


@blueprint.route('/user', methods=['GET'])
def handle_user():
    email = auth_api.auth()['email']
    user = database_api.user(email)
    return to_json(user)


def get_email_and_dataset(content):
    email = auth_api.auth()['email']
    dataset_id = content.get('id', '')
    if dataset_id == '':
        return 'Please supply an id', 400
    dataset = database_api.get_dataset(email, dataset_id)
    return email, dataset


@blueprint.route('/data', methods=['POST'])
def handle_data():
    json_request = request.get_json(cache=False)
    email, dataset = get_email_and_dataset(json_request)

    return to_json(
        data_processing.handle_data(dataset_api=dataset_api, dataset=dataset,
            embedding_list=json_request.get('embedding'),
            stats=json_request.get('stats'),
            grouped_stats=json_request.get('groupedStats'),
            selection=json_request.get('selection')))


@blueprint.route('/selection', methods=['POST'])
def handle_selection():
    # selection includes stats, coordinates
    content = request.get_json(cache=False)
    email, dataset = get_email_and_dataset(content)
    data_filter = content.get('filter')
    return to_json(data_processing.handle_selection(dataset_api=dataset_api, dataset=dataset, data_filter=data_filter,
        measures=content.get('measures', []), dimensions=content.get('dimensions', []),
        embeddings=content.get('embeddings', [])))


@blueprint.route('/selected_ids', methods=['POST'])
def handle_selected_ids():
    content = request.get_json(cache=False)
    email, dataset = get_email_and_dataset(content)
    data_filter = content.get('filter')
    return to_json(
        data_processing.handle_selection_ids(dataset_api=dataset_api, dataset=dataset, data_filter=data_filter))


# List available datasets
@blueprint.route('/datasets', methods=['GET'])
def handle_datasets():
    email = auth_api.auth()['email']
    return to_json(database_api.datasets(email))


@blueprint.route('/dataset', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_dataset():
    email = auth_api.auth()['email']
    # POST=new dataset, PUT=update dataset, DELETE=delete, GET=get dataset info
    if request.method == 'PUT' or request.method == 'POST':
        content = request.get_json(force=True, cache=False)
        dataset_id = content.get('id', '')
        if request.method == 'POST' and dataset_id == '':
            return 'Please supply an id', 400
        readers = set(content.get('readers', []))
        dataset_name = content.get('name', '')
        url = content.get('url', '')  # e.g. gs://foo/a/b/
        if dataset_name == '' or url == '':
            return 'Must supply dataset name and URL', 400
        dataset_id = database_api.upsert_dataset(email=email,
            dataset_id=dataset_id if request.method == 'PUT' else None,
            dataset_name=dataset_name, url=url, readers=readers)
        return to_json({'id': dataset_id})
    elif request.method == 'DELETE':
        content = request.get_json(force=True, cache=False)
        dataset_id = content.get('id', '')
        database_api.delete_dataset(email, dataset_id)
        return to_json('', 204)
    elif request.method == 'GET':
        dataset_id = request.args.get('id', '')
        return to_json(database_api.get_dataset(email, dataset_id, True))


    # if request.method == 'POST' or (request.method == 'PUT' and url != dataset_dict.get('url',
    #         '')):  # only check if can read on new dataset created
    # bucket = url[5:]  # remove gs://
    # slash = bucket.index('/')
    # gcp_object = urllib.parse.quote(bucket[slash + 1:], safe='')
    # bucket = urllib.parse.quote(bucket[0: slash], safe='')

    # head_request = requests.head(
    #     'https://www.googleapis.com/storage/v1/b/{bucket}/o/{object}'.format(bucket=bucket,
    #         object=gcp_object),
    #     headers={'Authorization': 'Bearer ' + request_util.credentials.get_access_token().access_token})
    # head_request.close()
    # if head_request.status_code != 200:
    #     return 'Not authorized to read {}'.format(url), 403
