import base64
import urllib
import warnings

from chromepdf.conf import parse_settings
from chromepdf.pdfconf import clean_pdf_kwargs
from chromepdf.webdrivers import (devtool_command,
                                  download_chromedriver_version,
                                  get_chrome_version, get_chrome_webdriver)


class ChromePdfMaker:
    """A class used to expedite PDF creation and storing of settings state."""

    def __init__(self, **kwargs):

        # load settings, combining those from **kwargs as well as the Django settings.
        settings = parse_settings(**kwargs)
        self._chrome_path = settings['chrome_path']
        self._chromedriver_path = settings['chromedriver_path']
        self._chromedriver_downloads = settings['chromedriver_downloads']

        # download chromedriver if we have chrome, and downloads are enabled
        if self._chrome_path is not None and self._chromedriver_path is None and self._chromedriver_downloads:
            chrome_version = get_chrome_version(self._chrome_path)
            self._chromedriver_path = download_chromedriver_version(chrome_version)

    def _clean_pdf_kwargs(self, pdf_kwargs):
        """A wrapper around clean_pdf_kwargs() that handles None as well."""

        pdf_kwargs = {} if pdf_kwargs is None else pdf_kwargs
        pdf_kwargs = clean_pdf_kwargs(**pdf_kwargs)
        return pdf_kwargs

    def generate_pdf(self, html, pdf_kwargs):
        """Generate a PDF file from an html string and return the PDF as a bytes object."""

        pdf_kwargs = self._clean_pdf_kwargs(pdf_kwargs)

        with get_chrome_webdriver(chrome_path=self._chrome_path, chromedriver_path=self._chromedriver_path) as driver:

            # we could put the html here. but data urls in Chrome are limited to 2MB.
            dataurl = "data:text/html;charset=utf-8," + urllib.parse.quote('')
            driver.get(dataurl)

            # append our html. theoretically no length limit. escapes all except ascii letters+numbers.
            html = html.replace('`', r'\`')  # escape the backtick used to indicate a multiline string in javascript
            # we do NOT need to escape any other chars (quotes, etc), including unicode
            driver.execute_script("document.write(`{}`)".format(html))

            result = devtool_command(driver, "Page.printToPDF", pdf_kwargs)

        outbytes = base64.b64decode(result['data'])
        return outbytes

    def generate_pdf_url(self, url, pdf_kwargs):
        """Generate a PDF file from a url (such as a file:/// url) and return the PDF as a bytes object."""

        warnings.warn("ChromePdfMaker.generate_pdf_url() is deprecated, use generate_pdf() instead.", DeprecationWarning)

        pdf_kwargs = self._clean_pdf_kwargs(pdf_kwargs)

        with get_chrome_webdriver(chrome_path=self._chrome_path, chromedriver_path=self._chromedriver_path) as driver:
            driver.get(url)
            result = devtool_command(driver, "Page.printToPDF", pdf_kwargs)

        outbytes = base64.b64decode(result['data'])
        return outbytes
