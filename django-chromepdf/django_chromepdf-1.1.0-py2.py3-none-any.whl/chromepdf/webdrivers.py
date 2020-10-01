import io
import json
import os
import platform
import subprocess
import zipfile
from contextlib import contextmanager
from subprocess import PIPE
from urllib import request as urllib_request

from selenium import webdriver

from chromepdf.exceptions import ChromePdfException


def get_chrome_version(path):
    """Return a 4-tuple containing the version number of the Chrome binary exe, EG for Chrome 85: (85,0,4183,121) """

    is_windows = (platform.system() == 'Windows')

    if is_windows:
        cmd = f'(Get-Item "{path}").VersionInfo'
        proc = subprocess.run(['powershell', cmd], stdout=PIPE, stderr=PIPE)
        # NOTE: "chrome.exe --version" does NOT work on windows. This is one workaround.
        # https://bugs.chromium.org/p/chromium/issues/detail?id=158372
        #
        # this will output a table like so. In this case, we want to grab the "85.0.4183.121"
        # ProductVersion   FileVersion      FileName
        # --------------   -----------      --------
        # 85.0.4183.121    85.0.4183.121    C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
        lines = [l.strip() for l in proc.stdout.decode('utf8').split('\n') if l.strip()]
        for l in lines:
            if l[0].isdigit():
                version = l.split()[0]
                return tuple(int(i) for i in version.split('.'))
    else:  # linux
        proc = subprocess.run([path, '--version'], stdout=PIPE, stderr=PIPE)
        version_stdout = proc.stdout.decode('utf8').strip()  # returns, eg, "Google Chrome 85.0.4183.121"
        version = [i for i in version_stdout.split() if i[0].isdigit()][0]
        return tuple(int(i) for i in version.split('.'))


def _get_chromedriver_download_path(major_version):
    """Return a path where a chromedriver file is/should be located."""

    assert isinstance(major_version, int)

    is_windows = (platform.system() == 'Windows')
    chromedrivers_dir = os.path.join(os.path.dirname(__file__), 'chromedrivers')
    chromedriver_path = os.path.join(chromedrivers_dir, f'chromedriver_{major_version}')
    if is_windows:
        chromedriver_path += '.exe'
    return chromedriver_path


def download_chromedriver_version(version, force=False):
    """
    See https://chromedriver.chromium.org/downloads/version-selection
    for download url api

    Arguments:
    * version: A 4-tuple version string as returned by get_chrome_version(), such as: (85,0,4183,121)
    * force: If True, will force a download, even if a driver for that version is already saved.
    """

    assert isinstance(version, tuple) and (isinstance(i, int) for i in version)

    version_major = version[0]

    chromedriver_download_path = _get_chromedriver_download_path(version_major)
    if os.path.exists(chromedriver_download_path) and not force:
        return chromedriver_download_path

    # Google's API for the latest release takes only the first 3 parts of the version
    version_first3parts = '.'.join(str(i) for i in version[:3])  # EG, 85.0.4183

    # This url returns a 4-part version string for which a chromedriver exists.
    url = f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_first3parts}'
    with urllib_request.urlopen(url) as f:
        contents = f.read()
    latest_version_str = contents.decode('utf8')  # EG 85.0.4183.87

    # These are the filenames of the chromedriver zip files for each OS.
    is_windows = (platform.system() == 'Windows')
    filename = 'chromedriver_win32.zip' if is_windows else 'chromedriver_linux64.zip'

    # Download the zip file
    url2 = f'https://chromedriver.storage.googleapis.com/{latest_version_str}/{filename}'
    with urllib_request.urlopen(url2) as f:
        zip_bytes = f.read()

    # open the zip file, find the chromedriver, and save it to the specified path.
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes), "r")
    for name in zf.namelist():
        if 'chromedriver' in name:
            with zf.open(name) as chromedriver_file:
                with open(chromedriver_download_path, 'wb') as f:
                    f.write(chromedriver_file.read())
                    os.chmod(chromedriver_download_path, 0o764)  # grant execute permission
                    return chromedriver_download_path

    raise ChromePdfException('Failed to download the chromedriver file.')


@contextmanager
def get_chrome_webdriver(chrome_path, chromedriver_path):
    """
    Create and return a Chrome webdriver. Is a context manager, and will automatically close the driver. Usage:

    * chromedriver_path: Path to your chromedriver executable. If None, will try to find it on PATH via Selenium.
    * chrome_path: Path to your Chrome exe. If None, driver will try to find it automatically.

    with get_chrome_webdriver(...) as driver:
        # call commands...
    # driver is automatically closed
    """

    # at one point "-disable-gpu" was required for headless Chrome. Keep it here just in case.
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    options.add_argument("--log-level=3")  # silence logging

    # silence the "DevTools started" message on windows
    # https://bugs.chromium.org/p/chromedriver/issues/detail?id=2907#c3
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if chrome_path is not None:
        options.binary_location = chrome_path  # Selenium API

    chrome_kwargs = {'options': options}
    if chromedriver_path is not None:
        chrome_kwargs['executable_path'] = chromedriver_path  # Selenium API

    # contextmanager.__enter__
    driver = webdriver.Chrome(**chrome_kwargs)
    yield driver

    # contextmanager.__exit__
    driver.close()


def devtool_command(driver, cmd, params={}):
    """
    Send a command to Chrome via the web driver.
    Example:
        result = devtool_command(driver, "Page.printToPDF", pdf_kwargs)
    """

    resource = f"/session/{driver.session_id}/chromium/send_command_and_get_result"
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    if 'status' in response:
        raise ChromePdfException(response.get('value'))
    return response.get('value')
