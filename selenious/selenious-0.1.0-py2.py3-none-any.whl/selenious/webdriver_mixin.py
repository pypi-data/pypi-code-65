from . import decorators
from .helpers import validate_time_settings


class WebDriverMixin:
    """
    Enhances the selenium.webdriver.remote.webdriver.WebDriver
    with several enhanced capabilities.
    """

    def __init__(self, *args, **kwargs):
        self._timeout = kwargs.get("timeout", 0)
        self._poll_frequency = kwargs.get("poll_frequency", 0.5)
        self._recover = kwargs.get("recover", None)
        self._debounce = kwargs.get("debounce", 0.0)
        self._implicitly_wait = kwargs.get("implicitly_wait", 0.0)
        validate_time_settings(
            self._implicitly_wait, self._timeout, self._poll_frequency
        )
        delete = ("timeout", "poll_frequency", "recover", "debounce")
        kwargs = {k: v for (k, v) in kwargs.items() if k not in delete}
        super().__init__(*args, **kwargs)

    def implicitly_wait(self, time_to_wait):
        """
        Sets a sticky timeout to implicitly wait for an element to be found,
           or a command to complete. This method only needs to be called one
           time per session. To set the timeout for calls to
           execute_async_script, see set_script_timeout.

        Warning: The selenious package will fail if implicitly_wait is larger
        than timeout or poll_frequency.  It is better to not set this and
        instead use the timeout property.

        :Args:
         - time_to_wait: Amount of time to wait (in seconds)

        :Usage:
            driver.implicitly_wait(30)
        """
        validate_time_settings(time_to_wait, self.timeout, self.poll_frequency)

        self._implicitly_wait = time_to_wait
        return super().implicitly_wait(time_to_wait)

    @property
    def timeout(self):
        """The default selenious timout.

        The selenium webdriver has an implicitly_wait() command that
        once set cannot be overwritten.  There is also a WebDriverWait()
        facility to allow requests with a wait.  This command moves
        an equivalent to that capability directly into the select commands.
        You can specify a global wait timeout with timeout property or pass
        a timeout parameter directly to the select command.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        validate_time_settings(self._implicitly_wait, timeout, self._poll_frequency)
        self._timeout = timeout

    @property
    def debounce(self):
        """The wait time for a select to have not changed."""
        return self._debounce

    @debounce.setter
    def debounce(self, debounce):
        self._debounce = debounce

    @property
    def poll_frequency(self):
        """The frequency polling will happen for the timeout.

        This is similar to the WebDriverWait polling frequency.  See
        set_timeout() for differences.
        """

        return self._poll_frequency

    @poll_frequency.setter
    def poll_frequency(self, poll_frequency):
        validate_time_settings(self._implicitly_wait, self.timeout, poll_frequency)

        self._poll_frequency = poll_frequency

    @property
    def recover(self):
        """The recover function.

        The recover function is run when a select fails or some
        actions like click fail.  The intent is to try to fix
        expected, but not typical web activities like an advertising
        popup covering the page being manipulated.

        The recovery function is guaranteed to be run at least once
        if there is an issue, but may be run multiple times at the
        poll_frequency if there is a timeout.

        :Args:
        - recover - The recover function to be run.  Parameters are:
          - webdriver - This webdriver (self)
          - function - The function calling the recover function.
          - kwargs - The kwargs sent to the function
          - elapsed - The time elapsed since the first attempt.
          - attempts - The number of attempts
        """
        return self._recover

    @recover.setter
    def recover(self, recover):
        self._recover = recover

    @decorators.find_element
    def find_element_by_id(self, *args, **kwargs):
        """Finds an element by id.

        :Args:
         - id_ - The id of the element to be found.

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_id('foo')
        """
        return super().find_element_by_id(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_id(self, *args, **kwargs):
        """
        Finds multiple elements by id.

        :Args:
         - id_ - The id of the elements to be found.

        :Returns:
         - list of WebElement - a list with elements if any was found.  An
           empty list if not

        :Usage:
            elements = driver.find_elements_by_id('foo')
        """
        return super().find_elements_by_id(*args, **kwargs)

    @decorators.find_element
    def find_element_by_xpath(self, *args, **kwargs):
        """
        Finds an element by xpath.

        :Args:
         - xpath - The xpath locator of the element to find.

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_xpath('//div/td[1]')
        """
        return super().find_element_by_xpath(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_xpath(self, *args, **kwargs):
        """
        Finds multiple elements by xpath.

        :Args:
         - xpath - The xpath locator of the elements to be found.

        :Returns:
         - list of WebElement - a list with elements if any was found.  An
           empty list if not

        :Usage:
            elements = driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return super().find_elements_by_xpath(*args, **kwargs)

    def find_element_by_link_text(self, *args, **kwargs):
        """
        Finds an element by link text.

        :Args:
         - link_text: The text of the element to be found.

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_link_text('Sign In')
        """
        return super().find_element_by_link_text(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_link_text(self, *args, **kwargs):
        """
        Finds elements by link text.

        :Args:
         - link_text: The text of the elements to be found.

        :Returns:
         - list of webelement - a list with elements if any was found.  an
           empty list if not

        :Usage:
            elements = driver.find_elements_by_link_text('Sign In')
        """
        return super().find_elements_by_link_text(*args, **kwargs)

    @decorators.find_element
    def find_element_by_partial_link_text(self, *args, **kwargs):
        """
        Finds an element by a partial match of its link text.

        :Args:
         - link_text: The text of the element to partially match on.

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_partial_link_text('Sign')
        """
        return super().find_element_by_partial_link_text(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_partial_link_text(self, *args, **kwargs):
        """
        Finds elements by a partial match of their link text.

        :Args:
         - link_text: The text of the element to partial match on.

        :Returns:
         - list of webelement - a list with elements if any was found.  an
           empty list if not

        :Usage:
            elements = driver.find_elements_by_partial_link_text('Sign')
        """
        return super().find_elements_by_partial_link_text(*args, **kwargs)

    @decorators.find_element
    def find_element_by_name(self, *args, **kwargs):
        """
        Finds an element by name.

        :Args:
         - name: The name of the element to find.

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_name('foo')
        """
        return super().find_element_by_name(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_name(self, *args, **kwargs):
        """
        Finds elements by name.

        :Args:
         - name: The name of the elements to find.

        :Returns:
         - list of webelement - a list with elements if any was found.  an
           empty list if not

        :Usage:
            elements = driver.find_elements_by_name('foo')
        """
        return super().find_elements_by_name(*args, **kwargs)

    @decorators.find_element
    def find_element_by_tag_name(self, *args, **kwargs):
        """
        Finds an element by tag name.

        :Args:
         - name - name of html tag (eg: h1, a, span)

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_tag_name('h1')
        """
        return super().find_element_by_tag_name(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_tag_name(self, *args, **kwargs):
        """
        Finds elements by tag name.

        :Args:
         - name - name of html tag (eg: h1, a, span)

        :Returns:
         - list of WebElement - a list with elements if any was found.  An
           empty list if not

        :Usage:
            elements = driver.find_elements_by_tag_name('h1')
        """
        return super().find_elements_by_tag_name(*args, **kwargs)

    @decorators.find_element
    def find_element_by_class_name(self, *args, **kwargs):
        """
        Finds an element by class name.

        :Args:
         - name: The class name of the element to find.

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_class_name('foo')
        """
        return super().find_element_by_class_name(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_class_name(self, *args, **kwargs):
        """
        Finds elements by class name.

        :Args:
         - name: The class name of the elements to find.

        :Returns:
         - list of WebElement - a list with elements if any was found.  An
           empty list if not

        :Usage:
            elements = driver.find_elements_by_class_name('foo')
        """
        return super().find_elements_by_class_name(*args, **kwargs)

    @decorators.find_element
    def find_element_by_css_selector(self, *args, **kwargs):
        """
        Finds an element by css selector.

        :Args:
         - css_selector - CSS selector string, ex: 'a.nav#home'

        :Returns:
         - WebElement - the element if it was found

        :Raises:
         - NoSuchElementException - if the element wasn't found

        :Usage:
            element = driver.find_element_by_css_selector('#foo')
        """
        return super().find_element_by_css_selector(*args, **kwargs)

    @decorators.find_elements
    def find_elements_by_css_selector(self, *args, **kwargs):
        """
        Finds elements by css selector.

        :Args:
         - css_selector - CSS selector string, ex: 'a.nav#home'

        :Returns:
         - list of WebElement - a list with elements if any was found.  An
           empty list if not

        :Usage:
            elements = driver.find_elements_by_css_selector('.foo')
        """
        return super().find_elements_by_css_selector(*args, **kwargs)

    @decorators.find_element
    def find_element(self, *args, **kwargs):
        """
        Find an element given a By strategy and locator. Prefer the find_element_by_*
        methods when possible.

        :Usage:
            element = driver.find_element(By.ID, 'foo')

        :rtype: WebElement
        """
        return super().find_element(*args, **kwargs)

    @decorators.find_elements
    def find_elements(self, *args, **kwargs):
        """
        Find elements given a By strategy and locator. Prefer the find_elements_by_*
        methods when possible.

        :Usage:
            elements = driver.find_elements(By.CLASS_NAME, 'foo')

        :rtype: list of WebElement
        """
        return super().find_elements(*args, **kwargs)
