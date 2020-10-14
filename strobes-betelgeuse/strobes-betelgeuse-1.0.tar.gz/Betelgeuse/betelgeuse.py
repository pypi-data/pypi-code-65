import urllib.request
import json
import time

from Betelgeuse.input import parse_args
from Betelgeuse.logging import get_logger
from Betelgeuse.exceptions import BuildFailureException

logger = get_logger()

headers = {'User-Agent': 'Strobes Betelugeuse Client',
           'Content-Type': 'application/json'}


def prepare_url(arguments):
    return f"{arguments.Scheme}://{arguments.Host}:{arguments.Port}{arguments.Path}"


def start_scan(arguments):
    url = prepare_url(arguments)
    success = False
    status = task_id = None
    try:
        headers['Authorization'] = arguments.Authorization
        if arguments.Target:
            post_data = json.dumps({'target': arguments.Target}).encode()

        else:
            post_data = "{}".encode()
        url = f'{url}/remote_access/{arguments.Remote_access}/scan/'
        request = urllib.request.Request(
            url=url, headers=headers, data=post_data)
        resp = urllib.request.urlopen(request)
        if resp.getcode() == 201:
            data = json.load(resp)
            status = data['status']
            task_id = data['task_id']
            logger.info(f"Task ID: {task_id}")
            success = True
            logger.info(f"Successfully started a scan.")
        return status, task_id, success
    except Exception as e:
        logger.error(e)
        return status, task_id, success


def scan_status(arguments, task_id):
    build_status = True
    status = 5
    url = prepare_url(arguments)
    try:
        url = f'{url}/remote_access/{arguments.Remote_access}/status/{task_id}/'
        request = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(request)
        if resp.getcode() == 200:
            data = json.load(resp)
            status = data['status']
            build_status = data['build_status']
        return status, build_status
    except Exception as e:
        logger.error(e)
        return status, False


def main():
    arguments = parse_args()
    logger.info(f"Remote Access ID: {arguments.Remote_access}")
    if arguments.Authorization and arguments.Target and arguments.Remote_access:
        status, task_id, success = start_scan(arguments)
        if (arguments.Wait is True) and (success is True):
            while status == 1:
                time.sleep(5)
                status, build_status = scan_status(arguments, task_id)
                if arguments.Exit and not build_status:
                    raise BuildFailureException

        return status


if __name__ == "__main__":
    main()
