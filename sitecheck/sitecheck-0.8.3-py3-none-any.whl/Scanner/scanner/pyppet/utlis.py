"""
    Utilities Package for Pyppet
"""
import logging
import os

from dateutil.parser import parse

logger = logging.getLogger('root')


def check_date(time) -> str:
    """
    Check time since the current time
    :param time:
    :return: Diffrence in seconds
    :rtype: int
    """
    now = parse(os.environ['Nowdate'])
    return int((now - parse(time)).total_seconds())


async def wait_type(page, selector, txt):
    """
    :param: page
    :param: selector
    :param: txt

    Wait for a selector to load than type supplied text.

    :returns: page
        This is in case the pages response to text changes the browser context.

    """
    await page.waitForSelector(selector)
    await page.type(selector, txt)
    return page


async def click(page, selector):
    """
    :param: page
    :param: selector

    Wait for a selector to load, than click on it.

    :returns: page
        This is in case click navigation changes the browser context.
    """
    await page.waitForSelector(selector),
    await page.click(selector)
    return page


async def wait_hover(page, selector):
    """
    :param: page
    :param: selector

    Wait for a selector to load, than hover over it.

    :returns: page
        This is in case page response changes the browser context.
    """
    await page.waitForSelector(selector),
    await page.hover(selector)
    return page


async def screenshot(self, sensor, name_sel):
    """

    :param self: 
    :param sensor: 
    :param name_sel: 
    :return: 
    """
    logger.warn('Feature is disabled')
    return
    # project_images = f"{os.environ['ROOT_DIR']}\\Screenshots\\{self.project.name}\\"
    # if os.path.exists(project_images):
    #     pass
    # else:
    #     os.makedirs(project_images)
    # await wait_hover(self.page, name_sel)
    # await self.page.waitFor(500)
    # await self.page.screenshot(
    #   {'path': project_images+sensor+'_'+get_date()+'.png'}
    #   )


def disable_timeout_pyppeteer():
    """
        :Pyppeteer upstream depricates need for this:
        Disables built-in max browser interation Timeout

        :returns: original_method(*args, **kwargs)
    """
    import pyppeteer.connection

    original_method = pyppeteer.connection.websockets.client.connect

    def new_method(*args, **kwargs):
        kwargs['ping_interval'] = None
        kwargs['ping_timeout'] = None
        return original_method(*args, **kwargs)

    pyppeteer.connection.websockets.client.connect = new_method


async def wait_count(self, count):
    """
    Wait for {count}, While printing seconds remanining
    :param self: Page context
    :param count: NUmber of seconds to wait
    :return: none
    """
    while count > 0:
        wait_time = str(count)
        print(f"Waiting {wait_time} seconds for Page load..")
        count -= 1
        await self.page.waitFor(1000)
    return
