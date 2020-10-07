import os
import requests
import logging

AUTH_TOKEN = os.environ.get('CANVAS_TOKEN')
CANVAS_URL = 'https://canvas.ox.ac.uk'
AUTH_HEADER = {'Authorization': 'Bearer ' + AUTH_TOKEN}

if AUTH_TOKEN is None:
    raise RuntimeError('Error: you must set AUTH_TOKEN environment variable')


def fetch_course_id(course_sis_id):
    logging.debug('Fetching course with sis id {}'.format(course_sis_id))
    payload = {}
    results = requests.get(CANVAS_URL +
                           '/api/v1/courses/sis_course_id:{}'.format(course_sis_id),
                           data=payload, headers=AUTH_HEADER)
    results.raise_for_status()
    results = results.json()
    return results['id']


def fetch_file_id(course_sis_id, file_name):
    logging.debug('Getting file list for course with sis id {} with name matching {}'.format(
        course_sis_id, file_name))
    payload = {'search_term': file_name}
    file_list = requests.get(CANVAS_URL +
                             '/api/v1/courses/sis_course_id:{}/files'.format(
                                 course_sis_id),
                             data=payload, headers=AUTH_HEADER)
    file_list.raise_for_status()
    file_list = file_list.json()

    if len(file_list) > 1:
        raise RuntimeError('More than one file matched name!')
    if len(file_list) == 0:
        raise RuntimeError('No file matched name!')

    return file_list[0]['id']


def search_modules(course_id, name):
    logging.debug('Searching for module in course {} with name {}'.format(
        course_id, name)
    )
    payload = {'search_term': name}
    results = requests.get(CANVAS_URL +
                           '/api/v1/courses/{}/modules'.format(course_id),
                           data=payload, headers=AUTH_HEADER)
    results.raise_for_status()
    modules = results.json()

    return modules


def create_module(course_id, name):
    logging.info('Creating module in course {} with name {}'.format(course_id, name))
    payload = {
        'module[name]': name,
    }
    result = requests.post(CANVAS_URL +
                           '/api/v1/courses/{}/modules'.format(course_id),
                           data=payload, headers=AUTH_HEADER)
    result.raise_for_status()
    module = result.json()

    return module['id']


def delete_module(course_id, module_id):
    logging.info('Deleting module {}'.format(course_id, module_id))
    payload = {}
    result = requests.delete(CANVAS_URL +
                           '/api/v1/courses/{}/modules/{}'.format(course_id, module_id),
                           data=payload, headers=AUTH_HEADER)
    result.raise_for_status()
    module = result.json()

    return module['id']


def add_module_items(course_id, module_id, module_items):
    logging.info('Adding module items {} to module {} in course {}'.format(
        module_items, module_id, course_id)
    )
    for item in module_items:
        add_module_item(course_id, module_id, item)


def add_module_item(course_id, module_id, item, indent=0):
    logging.debug('Adding module item {} to module {} in course {}'.format(
        item, module_id, course_id)
    )
    payload = {}
    for k, v in item.items():
        if k != 'sub_items':
            payload['module_item[{}]'.format(k)] = v
    payload['module_item[indent]'] = indent

    result = requests.post(CANVAS_URL +
                           '/api/v1/courses/{}/modules/{}/items'.format(
                               course_id, module_id
                           ),
                           data=payload, headers=AUTH_HEADER)
    result.raise_for_status()

    if 'sub_items' in item.keys():
        for sub_item in item['sub_items']:
            add_module_item(course_id, module_id, sub_item, indent=indent+1)


def regenerate_module(course_sis_id, course_items):
    course_id = fetch_course_id(course_sis_id)
    for i in course_items:
        modules = search_modules(course_id, i['module_name'])
        if len(modules) > 1:
            raise RuntimeError('Too many modules matched name!')
        if len(modules) == 1:
            delete_module(course_id, modules[0]['id'])

        module_id = create_module(course_id, i['module_name'])
        add_module_items(course_id, module_id, i['module_content'])
