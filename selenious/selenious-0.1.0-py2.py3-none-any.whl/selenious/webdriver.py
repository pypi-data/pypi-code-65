from selenium.webdriver import Firefox, FirefoxProfile, FirefoxOptions  # noqa: F401
from selenium.webdriver import Chrome, ChromeOptions  # noqa: F401
from selenium.webdriver import Ie, IeOptions  # noqa: F401
from selenium.webdriver import Edge
from selenium.webdriver import Opera
from selenium.webdriver import Safari
from selenium.webdriver import BlackBerry
from selenium.webdriver import PhantomJS
from selenium.webdriver import Android
from selenium.webdriver import WebKitGTK, WebKitGTKOptions  # noqa: F401
from selenium.webdriver import Remote
from selenium.webdriver import DesiredCapabilities  # noqa: F401
from selenium.webdriver import ActionChains  # noqa: F401
from selenium.webdriver import TouchActions  # noqa: F401
from selenium.webdriver import Proxy  # noqa: F401
from .webdriver_mixin import WebDriverMixin


class Firefox(WebDriverMixin, Firefox):
    pass


class Chrome(WebDriverMixin, Chrome):
    pass


class Ie(WebDriverMixin, Ie):
    pass


class Edge(WebDriverMixin, Edge):
    pass


class Opera(WebDriverMixin, Opera):
    pass


class Safari(WebDriverMixin, Safari):
    pass


class BlackBerry(WebDriverMixin, BlackBerry):
    pass


class PhantomJS(WebDriverMixin, PhantomJS):
    pass


class Android(WebDriverMixin, Android):
    pass


class WebKitGTK(WebDriverMixin, WebKitGTK):
    pass


class Remote(WebDriverMixin, Remote):
    pass
