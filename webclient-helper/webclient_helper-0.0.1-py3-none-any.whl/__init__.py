import fs_helper as fh
import requests
import time
import warnings
from json import JSONDecodeError
from urllib.parse import urlparse
try:
    from bs4 import BeautifulSoup, FeatureNotFound
    import os.path
except ImportError:
    BeautifulSoup = None


logger = fh.get_logger(__name__)


def get_domain(url):
    """Return the domain of a url"""
    return urlparse(url).netloc.replace('www.', '')


def new_requests_session(username=None, password=None, user_agent=None,
                         content_type=None, extra_headers={}):
    """Return a new requests Session object

    - username: if specified, set auth on session (requires password)
    - password: if specified, set auth on session (requires username)
    - user_agent: if specified, set "User-Agent" header on session
    - content_type: if specified, set "Content-Type" header on session
    - extra_headers: a dict of extra_headers to set on the session

    Both username and password required to set auth (for basic auth)
    """
    if username and not password:
        raise Exception('You must specify a password if passing a username')
    elif password and not username:
        raise Exception('You must specify a username if passing a password')
    session = requests.Session()
    if user_agent:
        extra_headers['User-Agent'] = user_agent
    if content_type:
        extra_headers['Content-Type'] = content_type
    if username and password:
        session.auth = (username, password)
    session.headers.update(extra_headers)
    logger.debug('New session created')
    return session


def get_summary_from_response(response):
    """Return a string of info from a response object"""
    message_parts = [
        str(response.status_code),
        response.request.method,
        response.request.url,
        'in {} seconds'.format(response.elapsed.total_seconds()),
    ]
    return ' '.join(message_parts)


def OPTIONS(url, session=None, debug=False):
    """Send a OPTIONS request and return response object

    - url: url/endpoint
    - session: a session object
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.options(url)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def HEAD(url, session=None, debug=False):
    """Send a HEAD request and return response object

    - url: url/endpoint
    - session: a session object
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.head(url)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def GET(url, session=None, params=None, debug=False):
    """Send a GET request and return response data

    - url: url/endpoint
    - session: a session object
    - params: a dict with query string vars and values
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.get(url, params=params)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session" or "params"')
        return
    logger.debug(get_summary_from_response(response))
    try:
        data = response.json()
    except JSONDecodeError:
        data = response.content
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response" or "data"')
    return data


def POST(url, session=None, data=None, json=None, debug=False):
    """Send a POST request and return response object

    - url: url/endpoint
    - session: a session object
    - data: a dict to send in the body (non-JSON)
    - json: a dict to send in the body
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.post(url, data=data, json=json)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session", "data", or "json"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def PUT(url, session=None, data=None, debug=False):
    """Send a PUT request and return response object

    - url: url/endpoint
    - session: a session object
    - data: a dict to send in the body (non-JSON)
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.put(url, data=data)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session" or "data"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def PATCH(url, session=None, data=None, debug=False):
    """Send a PATCH request and return response object

    - url: url/endpoint
    - session: a session object
    - data: a dict to send in the body (non-JSON)
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.patch(url, data=data)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session" or "data"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def DELETE(url, session=None, debug=False):
    """Send a DELETE request and return response object

    - url: url/endpoint
    - session: a session object
    - debug: if True, enter debugger before returning
    """
    session = session or new_requests_session()
    try:
        response = session.delete(url)
    except requests.exceptions.ConnectionError as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "session"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def get_soup(url_or_file, session=None, warn=True):
    """Fetch url (or open a file) and return a BeautifulSoup object (or None)

    - url_or_file: a string
    - session: a session object
    - warn: if True, issue a warning if bs4 package is not installed
    """
    if BeautifulSoup is None:
        if warn:
            warnings.warn('The "beautifulsoup4" package is not installed!')
        return
    html = ''
    if os.path.isfile(url_or_file):
        with open(url_or_file, 'r') as fp:
            html = fp.read()
    else:
        html = GET(url_or_file, session)

    if html:
        try:
            return BeautifulSoup(html, 'lxml')
        except FeatureNotFound:
            return BeautifulSoup(html)


def download_file(url, localfile='', session=None):
    """Download file using `requests` with stream enabled

    - url: a string
    - localfile: a string
    - session: a session object

    See: http://stackoverflow.com/questions/16694907/
    """
    session = session or new_requests_session()
    localfile = localfile or fh.lazy_filename(url)

    for sleeptime in [5, 10, 30, 60]:
        try:
            logger.info('Saving {} to {}'.format(repr(url), repr(localfile)))
            r = session.get(url, stream=True)
            with open(localfile, 'wb') as fp:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        fp.write(chunk)
                        fp.flush()

            break
        except Exception as e:
            logger.error('{}... sleeping for {} seconds'.format(repr(e), sleeptime))
            session.close()
            time.sleep(sleeptime)
            session = new_requests_session()


from .client import *
