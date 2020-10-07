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


def add_module_items(course_id, module_id, module_items, assignments):
    logging.info('Adding module items {} to module {} in course {}'.format(
        module_items, module_id, course_id)
    )
    for item in module_items:
        add_module_item(course_id, module_id, item, assignments)


def add_module_item(course_id, module_id, item, assignments, indent=0):
    logging.debug('Adding module item {} to module {} in course {}'.format(
        item, module_id, course_id)
    )

    # replace content_id with canvas id we stored in assignments
    if 'content_id' in item.keys():
        for a in assignments:
            if a['name'] == item['content_id']:
                item['content_id'] = a['content_id']

    payload = {'search_term': item['title']}
    results = requests.get(CANVAS_URL +
                           '/api/v1/courses/{}/modules/{}/items'.format(
                               course_id, module_id
                           ),
                           data=payload, headers=AUTH_HEADER)
    results.raise_for_status()

    # check if module item already exists
    payload = {}
    for k, v in item.items():
        if k == 'completion_requirement':
            payload['module_item[{}][type]'.format(k)] = v['type']
        else:
            if k != 'sub_items':
                payload['module_item[{}]'.format(k)] = v
    payload['module_item[indent]'] = indent

    result_json = results.json()
    if len(result_json) == 0:
        # create new item
        result = requests.post(CANVAS_URL +
                               '/api/v1/courses/{}/modules/{}/items'.format(
                                   course_id, module_id
                               ),
                               data=payload, headers=AUTH_HEADER)
        result.raise_for_status()
    else:
        # update existing item
        item_id = result_json[0]['id']
        result = requests.put(CANVAS_URL +
                              '/api/v1/courses/{}/modules/{}/items/{}'.format(
                                  course_id, module_id, item_id
                              ),
                              data=payload, headers=AUTH_HEADER)
        result.raise_for_status()

    if 'sub_items' in item.keys():
        for sub_item in item['sub_items']:
            add_module_item(course_id, module_id, sub_item, assignments, indent=indent + 1)


def add_assignment(course_id, assignment, position):
    logging.debug('Adding assignment {} to course {}'.format(
        assignment, course_id)
    )
    payload = {'search_term': assignment['name']}
    results = requests.get(CANVAS_URL +
                           '/api/v1/courses/{}/assignments'.format(course_id),
                           data=payload, headers=AUTH_HEADER)
    results.raise_for_status()

    result_json = results.json()

    payload = {}
    for k, v in assignment.items():
        if k != 'sub_items':
            payload['assignment[{}]'.format(k)] = v
    payload['assignment[position]'] = position

    if len(result_json) == 0:
        result = requests.post(CANVAS_URL +
                               '/api/v1/courses/{}/assignments'.format(
                                   course_id
                               ),
                               data=payload, headers=AUTH_HEADER)
        result.raise_for_status()
    else:
        assignment_id = result_json[0]['id']
        result = requests.put(CANVAS_URL +
                              '/api/v1/courses/{}/assignments/{}'.format(
                                  course_id, assignment_id
                              ),
                              data=payload, headers=AUTH_HEADER)
        result.raise_for_status()

    assignment['content_id'] = result.json()['id']


def regenerate_module(course_sis_id, course_items, assignments):
    course_id = fetch_course_id(course_sis_id)
    for i, a in enumerate(assignments):
        add_assignment(course_id, a, i)

    for i in course_items:
        modules = search_modules(course_id, i['module_name'])
        if len(modules) > 1:
            raise RuntimeError('Too many modules matched name!')
        if len(modules) == 0:
            module_id = create_module(course_id, i['module_name'])
        else:
            module_id = modules[0]['id']

        add_module_items(course_id, module_id, i['module_content'], assignments)
