"""# API"""

from selenium.webdriver.common.keys import Keys

from datetime import datetime

def send_datetime(input_, datetime_):
    """
    Send a datetime object to a form input.

    Parameters
    ----------
    input_ : selenium.webdriver.remote.webelement.WebElement
        The form input to which the datetime object will be sent.

    datetime_ : datetime.datetime
        The datetime object to be sent.
    """
    return html_selenium[input_.get_attribute('type')](input_, datetime_)

def _send_date(input_, datetime_):
    return input_.send_keys(datetime_.strftime('%m%d%Y'))

def _send_datetime_local(input_, datetime_):
    date = datetime_.strftime('%m%d%Y')
    time = datetime_.strftime('%I%M%p')
    return input_.send_keys(date, Keys.TAB, time)

def _send_month(input_, datetime_):
    month = datetime_.strftime('%B')
    year = datetime_.strftime('%Y')
    return input_.send_keys(month, Keys.TAB, year)

def _send_time(input_, datetime_):
    return input_.send_keys(datetime_.strftime('%I%M%p'))

def _send_week(input_, datetime_):
    return input_.send_keys(datetime_.strftime('%U%Y'))

html_selenium = {
    'date': _send_date,
    'datetime-local': _send_datetime_local,
    'month': _send_month,
    'time': _send_time,
    'week': _send_week,
}

def get_datetime(input_type, response):
    """
    Get a datetime object from a form response after a POST request.

    Parameters
    ----------
    input_type : str
        Type of the input tag.

    response : str
        Response to the input tag.

    Returns
    -------
    datetime : datetime.datetime
        The response converted to a datetime object if possible, otherwise 
        the raw response. This method will fail to convert the response if 
        the input type is invalid or if the client did not enter a response 
        in this input tag.
    """
    format_ = html_datetime.get(input_type)
    return (
        datetime.strptime(response, format_) if response and format_
        else response
    )

html_datetime = {
    'date': '%Y-%m-%d',
    'datetime-local': '%Y-%m-%dT%H:%M',
    'month': '%Y-%m',
    'time': '%H:%M',
    'week': '%Y-W%W'
}