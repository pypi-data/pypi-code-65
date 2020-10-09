import asyncio
import os
from typing import List, Dict, Tuple, Union
import sys
import http.server
import socketserver
import urllib
import posixpath
import threading
import itertools

# This is a copy of the pyppeteer function in pyppeteer/chromium_downloader,
# but since we're trying to update the environment variables which are read in that file
# we can't import it
def pyppeteer_current_platform() -> str:
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    elif (sys.platform.startswith('win') or
          sys.platform.startswith('msys') or
          sys.platform.startswith('cyg')):
        if sys.maxsize > 2 ** 31 - 1:
            return 'win64'
        return 'win32'
    raise OSError('Unsupported platform: ' + sys.platform)

if not ('PYPPETEER_CHROMIUM_REVISION' in os.environ):
  plt = pyppeteer_current_platform()
  if plt == 'win32':
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = '798057'
  elif plt == 'win64':
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = '803555'
  elif plt == 'linux':
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = '798580'
  elif plt == 'mac':
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = '798027'
if not ('PYPPETEER_DOWNLOAD_HOST' in os.environ):
  os.environ['PYPPETEER_DOWNLOAD_HOST'] = 'http://storage.googleapis.com'
import pyppeteer
import logging

logger = logging.getLogger(__name__)

app_build_path = os.path.abspath(os.path.expanduser(__file__ + '/../app_build'))
app_build_index_html = os.path.join(app_build_path, 'index.html')

class AppBuildRequestHandler(http.server.SimpleHTTPRequestHandler):
  def translate_path(self, path):
      path = path.split('?',1)[0]
      path = path.split('#',1)[0]
      if path == '/':
        path = '/index.html'
      return app_build_path + '/' + path

class DerkAppInstance:
  """Application instance of "Dr. Derk's Mutant Battlegrounds"

  Args:
    headless: Run in headless mode
    app_host: Configure an alternative app bundle host. (Environment variable: DERK_APP_HOST)
    chrome_executable: Path to chrome or chromium. (Environment variable: DERK_CHROME_EXECUTABLE)
    chrome_args: List of command line switches passed to chrome
    chrome_devtools: Launch devtools when chrome starts
    browser: A pyppeteer browser instance
    browser_logs: Show log output from browser
    web_socket_worker: Run websockets in a web worker

  """
  def __init__(self,
      app_host: str=None,
      headless: bool=False,
      chrome_executable: str=None,
      chrome_args: List[str]=[],
      chrome_devtools: bool=False,
      browser: pyppeteer.browser.Browser=None,
      browser_logs: bool=False,
      internal_http_server: bool = False):

    self.app_host = app_host if app_host is not None else os.environ.get('DERK_APP_HOST', ('file://' + app_build_index_html))
    self.headless = headless
    self.chrome_executable = chrome_executable if chrome_executable is not None else os.environ.get('DERK_CHROME_EXECUTABLE', None)
    self.chrome_args = chrome_args
    self.chrome_devtools = chrome_devtools
    self.browser = browser
    self.browser_logs = browser_logs
    self.internal_http_server = internal_http_server

    self.logger = logger.getChild('DerkAppInstance')

    if self.internal_http_server:
      self.bundle_server = socketserver.TCPServer(('', 0), AppBuildRequestHandler)
      threading.Thread(target=self.bundle_server.serve_forever, daemon=True).start()
      self.app_host = 'http://localhost:' + str(self.bundle_server.server_address[1])

    self.page = None
    self.browser = None

  async def close(self):
    """Shut down app instance
    """
    self.logger.info('[close] Closing instance')
    if self.browser:
      await self.browser.close()
    if self.internal_http_server:
      self.bundle_server.shutdown()
    self.logger.info('[close] Done')

  async def start(self):
    """Start the application"""
    self.logger.info('[init] Using bundle host: ' + self.app_host)
    if not self.browser:
      self.logger.info('[init] Creating browser')
      chromium_args = [
        '--app=' + self.app_host,
        '--allow-file-access-from-files',
        '--disable-web-security',
        '--no-sandbox',
        '--ignore-gpu-blacklist',
        '--user-data-dir=' + os.environ.get('DERK_CHROMEDATA', './chromedata')
      ] + self.chrome_args
      if (self.headless):
        chromium_args.append('--use-gl=egl')
      self.browser = await pyppeteer.launch(
        ignoreHTTPSErrors=True,
        headless=self.headless,
        executablePath=self.chrome_executable,
        args=chromium_args,
        defaultViewport=None,
        devtools=self.chrome_devtools,
        handleSIGHUP=False,
        handleSIGTERM=False,
        handleSIGINT=False,
      )
      self.logger.info('[init] Creating browser ok')
    self.logger.info('[init] Getting page')
    self.page = [page for page in (await self.browser.pages()) if (not page.url.startswith('devtools'))][0]
    backend = os.environ.get('DERK_BACKEND', 'production')
    if backend is not None:
      self.logger.info('[init] Setting backend')
      await self.page.evaluateOnNewDocument('''(backend) => window.localStorage.setItem('backend', backend)''', backend)
    if self.browser_logs:
      self.logger.info('[init] Setting up logs')
      self.page.on('console', self._handle_console)
      self.page.on('error', lambda m: self.logger.error('[error] %s', m))
      self.page.on('pageerror', lambda m: self.logger.error('[pageerror] %s', m))
      self.page.on('requestfailed', lambda m: self.logger.error('[requestfailed] %s', m))
    self.logger.info('[init] Navigating to bundle host')
    await self.page.goto(self.app_host)
    self.logger.info('[init] Waiting for GymLoaded')
    await self.page.waitForSelector('.GymLoaded')
    self.logger.info('[init] Gym loaded ok')
    self.logger.info('[init] Done!')

  async def run_session(self, **kwargs):
    """Creates a session and runs episodes loop.

    See :meth:`create_session` for args.
    """
    await self.create_session(**kwargs)
    await self.run_episodes_loop()

  async def create_session(self,
      home_team: List[Dict]=None,
      away_team: List[Dict]=None,
      reward_function: Dict=None,
      n_arenas: int=1,
      substeps: int=8,
      turbo_mode: bool=False,
      interleaved: bool=True,
      agent_hosts: Union[List[Dict], str]=None,
      debug_no_observations: bool=False,
      web_socket_worker: bool=None):
    """Create a session

    All arguments are optional.

    Args:
      home_team: Home team creatures
      away_team: Away team creatures
      reward_function: Reward function. See :ref:`reward-function` for available options
      n_arenas: Number of parallel arenas to run
      substeps: Number of game steps to run for each call to step
      turbo_mode: Skip rendering to the screen to run as fast as possible. (Environment variable: DERK_TURBO_MODE)
      interleaved: Run each step in the background, returning the previous steps observations
      agent_hosts: List of DerkAgentServer's to connect to, or ``"single_local"``, or ``"dual_local"``. See below for details.

    With the interleaved mode on, there's a delay between observation and action of size substeps.
    E.g. if substeps=8 there's an 8*16ms = 128ms "reaction time" from observation to action. This means
    that the game and the python code can in effect run in parallel. This is always enabled in battles.

    The ``agent_hosts`` argument takes list of dicts with the following format:
    ``{ uri: str, regions: [{ side: str, start_arena: int, n_arenas: int }] }``, where
    ``uri`` specifies a running DerkAgentServer to connect to, and regions define which arenas and sides
    that agent will control.
    ``side`` can be ``'home'``, ``'away'`` or ``'both'``. ``start_arena`` and ``n_arenas`` can be ommitted
    to run the agent on all arenas. You can also pass a string value of ``"single_local"``, in which case
    the ``agent_hosts`` defaults to ``[{ 'uri': 'ws://127.0.0.1:8788', 'regions': [{ 'sides': 'both' }] }]``,
    or if you specify ``"dual_local"`` it defaults to

    .. code-block:: python

      [
        { 'uri': 'ws://127.0.0.1:8788', 'regions': [{ 'sides': 'home' }] },
        { 'uri': 'ws://127.0.0.1:8789', 'regions': [{ 'sides': 'away' }] }
      ]

    """
    if agent_hosts == 'single_local' or agent_hosts is None:
      agent_hosts = [{ 'uri': 'ws://127.0.0.1:8788', 'regions': [{ 'sides': 'both' }] }]
    elif agent_hosts == 'dual_local':
      agent_hosts = [
        { 'uri': 'ws://127.0.0.1:8788', 'regions': [{ 'sides': 'home' }] },
        { 'uri': 'ws://127.0.0.1:8789', 'regions': [{ 'sides': 'away' }] }
      ]
    config = {
      'agentHosts': agent_hosts,
      'home': home_team,
      'away': away_team,
      'rewardFunction': reward_function,
      'nArenas': n_arenas,
      'substeps': substeps,
      'turboMode': turbo_mode,
      'interleaved': interleaved,
      'debugNoObservations': debug_no_observations,
      'webSocketWorkers': web_socket_worker
    }
    self.logger.info('[run_session] Creting session')
    await self.page.evaluate('''(config) => window.derk.createSession(config)''', config)
    self.logger.info('[run_session] Session created')

  async def run_episodes_loop(self):
    """Runs episodes in a loop until agents disconnect"""
    self.logger.info('[run_episodes_loop] Starting loop')
    await self.page.evaluate('''() => window.derk.session.runEpisodesLoop()''')
    self.logger.info('[run_episodes_loop] Done')

  async def run_episode(self):
    """Run a single episode"""
    self.logger.info('[run_episode] Running')
    await self.page.evaluate('''() => window.derk.session.runEpisode()''')
    self.logger.info('[run_episode] Done')

  async def reload(self):
    """Reload the game"""
    await self.page.reload()
    self.logger.info('[run_session] Waiting for GymLoaded')
    await self.page.waitForSelector('.GymLoaded')
    self.logger.info('[run_session] Gym loaded ok')

  @property
  def running(self):
    """Returns true if the app is still running"""
    return self.browser.process.poll() is None

  def _handle_console(self, m):
    if m.type == 'error':
      self.logger.error('[console] %s', m.text)
    elif m.type == 'warning':
      self.logger.warning('[console] %s', m.text)
    else:
      self.logger.info('[console] %s', m.text)

  def get_webgl_renderer(self) -> str:
    """Return which webgl renderer is being used by the game"""
    return asyncio.get_event_loop().run_until_complete(self.async_get_webgl_renderer())

  async def async_get_webgl_renderer(self):
    """Async version of :meth:`get_webgl_renderer`"""
    return await self.page.evaluate('''() => window.derk.getWebGLRenderer()''')
