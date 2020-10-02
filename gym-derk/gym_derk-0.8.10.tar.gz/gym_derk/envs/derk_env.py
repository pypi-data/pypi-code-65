import gym
import asyncio
import os
from typing import List, Dict, Tuple
import sys
import http.server
import socketserver
import urllib
import posixpath
import threading
import json
import websockets

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
import numpy as np
from random import random
import webbrowser
import logging

logger = logging.getLogger(__name__)

app_build_path = os.path.abspath(os.path.expanduser(__file__ + '/../../app_build'))
app_build_index_html = os.path.join(app_build_path, 'index.html')

class AppBuildRequestHandler(http.server.SimpleHTTPRequestHandler):
  def translate_path(self, path):
      path = path.split('?',1)[0]
      path = path.split('#',1)[0]
      if path == '/':
        path = '/index.html'
      return app_build_path + '/' + path

class ConnectionLostError(Exception):
  def __init__(self, env):
    self.env = env

DerkEnvList = List[Tuple[str, List[Tuple[str, int, int]]]]

ENVS_SINGLE_LOCAL: DerkEnvList = [['ws://127.0.0.1:8788', [['both', 0, -1]]]]
ENVS_DUAL_LOCAL: DerkEnvList = [['ws://127.0.0.1:8788', [['home', 0, -1]]], ['ws://127.0.0.1:8789', [['away', 0, -1]]]]

class DerkEnv(gym.Env):
  """Reinforcement Learning environment for "Dr. Derk's Mutant Battlegrounds"

  There are three modes for the environment:

  * ``mode="normal"``: You control both the home and away teams.
  * ``mode="server"``: You control the home team, and other environments can connect to you through websockets.
  * ``mode="connected"``: Connects to an environment running in "server" mode.
    You control the home team, and the away team is controlled by the server environment.

  Args:
    mode: ``"normal"`` (default), ``"server"`` or ``"connected"``. See above for details. (Environment variable: DERK_MODE)
    server_port: Set port in server mode. Defaults to 8789. (Environment variable: DERK_SERVER_PORT)
    server_host: Set host in server mode. Defaults to "127.0.0.1". (Environment variable: DERK_SERVER_HOST)
    connected_host: Host to connect to in "connected" mode. Defaults to "ws://127.0.0.1:8789". (Environment variable: DERK_CONNECTED_HOST)
    app_host: Configure an alternative app bundle host. (Environment variable: DERK_APP_HOST)
    home_team: Home team creatures
    away_team: Away team creatures
    reward_function: Reward function. See :ref:`reward-function` for available options
    dummy_mode: Don't actually run the game, but just return random outputs
    n_arenas: Number of parallel arenas to run
    substeps: Number of game steps to run for each call to step
    turbo_mode: Skip rendering to the screen to run as fast as possible. (Environment variable: DERK_TURBO_MODE)
    interleaved: Run each step in the background, returning the previous steps observations
    headless: Run in headless mode
    chrome_executable: Path to chrome or chromium. (Environment variable: DERK_CHROME_EXECUTABLE)
    chrome_args: List of command line switches passed to chrome
    chrome_devtools: Launch devtools when chrome starts
    browser: A pyppeteer browser instance
    browser_logs: Show log output from browser
    safe_reset: A safer but slower version of reset. Use this if you get CONTEXT_LOST errors. (Environment variable: DERK_SAFE_RESET)
    no_init_browser: You need to run env.async_init_browser() manually to launch the browser if this is set to true
    web_socket_worker: Run websockets in a web worker

  With the interleaved mode on, there's a delay between observation and action of size substeps.
  E.g. if substeps=8 there's an 8*16ms = 128ms "reaction time" from observation to action. This means
  that the game and the python code can in effect run in parallel. This is always enabled in battles.

  Attributes:
    n_teams: Number of teams controlled by this environment
    n_agents_per_team: Number of agents in a team (3)
    n_actions: Number of actions per creature (5)
    total_reward: Accumulated rewards over an episode
    episode_stats: Stats for the last episode

  """
  def __init__(self,
      mode: str=False, server_port: int=None, server_host: str=None, connected_host: str=None,
      app_host: str=None,
      home_team: List[Dict] = None, away_team: List[Dict] = None, reward_function: Dict=None,
      dummy_mode: bool=False, n_arenas: int=1, substeps: int=8, turbo_mode: bool=False,
      interleaved: bool=True,
      headless: bool=False, chrome_executable: str=None, chrome_args: List[str]=[],
      chrome_devtools: bool=False,
      browser: pyppeteer.browser.Browser=None,
      safe_reset: bool=None, no_init_browser: bool=False, browser_logs: bool=False,
      debug_no_observations: bool=False, internal_http_server: bool = False, web_socket_worker: bool=None):

    self.mode = mode if mode is not None else os.environ.get('DERK_MODE', 'normal')
    self.server_host = server_host if server_host is not None else os.environ.get('DERK_SERVER_HOST', '127.0.0.1')
    self.server_port = server_port if server_port is not None else os.environ.get('DERK_SERVER_PORT', 8789 if mode == 'server' else 8788)
    self.connected_host = connected_host if connected_host is not None else os.environ.get('DERK_CONNECTED_HOST', 'ws://127.0.0.1:8789')
    self.app_host = app_host if app_host is not None else os.environ.get('DERK_APP_HOST', ('file://' + app_build_index_html))
    self.home_team = home_team
    self.away_team = away_team
    self.reward_function = reward_function
    self.dummy_mode = dummy_mode
    self.n_arenas = n_arenas
    self.substeps = substeps
    self.turbo_mode = turbo_mode if turbo_mode is not None else (os.environ.get('DERK_TURBO_MODE', 'False').lower() == 'true')
    self.interleaved = interleaved
    self.headless = headless
    self.chrome_executable = chrome_executable if chrome_executable is not None else os.environ.get('DERK_CHROME_EXECUTABLE', None)
    self.chrome_args = chrome_args
    self.chrome_devtools = chrome_devtools
    self.browser = browser
    self.browser_logs = browser_logs
    self.safe_reset = safe_reset if safe_reset is not None else (os.environ.get('DERK_SAFE_RESET', 'False').lower() == 'true')
    self.debug_no_observations = debug_no_observations
    self.internal_http_server = internal_http_server
    self.web_socket_worker = web_socket_worker if web_socket_worker is not None else (os.environ.get('DERK_WEB_SOCKET_WORKER', 'False').lower() == 'true')

    if self.internal_http_server:
      self.bundle_server = socketserver.TCPServer(('', 0), AppBuildRequestHandler)
      threading.Thread(target=self.bundle_server.serve_forever, daemon=True).start()
      self.app_host = 'http://localhost:' + str(self.bundle_server.server_address[1])

    self.page = None
    self.browser = None

    self.remote_connection = asyncio.Future()
    start_server = websockets.serve(self._handle_websocket, self.server_host, self.server_port, max_size=None)
    self.websocket_server = asyncio.get_event_loop().run_until_complete(start_server)
    self.remote_messages = asyncio.Queue()
    self.logger = logger.getChild('DerkEnv({})'.format(self.server_port))
    self.logger.info('Serving on ws://' + self.server_host + ':' + str(self.server_port))

    self.n_teams = 0
    self.n_agents_per_team = 3
    self.n_senses = 64
    self.n_actions = 5
    self.total_reward = None
    self.episode_stats = { 'homeWins': 0, 'awayWins': 0, 'ties': 0 }
    self.running_episode = None

    self.observation_space = gym.spaces.Box(low=-1, high=1, shape=[self.n_senses])
    self.action_space = gym.spaces.Tuple((
      gym.spaces.Box(low=-1, high=1, shape=[]), # MoveX
      gym.spaces.Box(low=-1, high=1, shape=[]), # Rotate
      gym.spaces.Box(low=0, high=1, shape=[]), # ChaseFocus
      gym.spaces.Discrete(4), # CastingSlot
      gym.spaces.Discrete(8), # ChangeFocus
    ))

    if (not self.dummy_mode and not no_init_browser and self.mode != 'server'):
      asyncio.get_event_loop().run_until_complete(self.async_init_browser())
    asyncio.get_event_loop().run_until_complete(self.remote_connection)

  @property
  def n_agents(self):
    """Number of agents controlled by this environment

    I.e. ``env.n_teams * env.n_agents_per_team``
    """
    return self.n_teams * self.n_agents_per_team

  def reset(self) -> np.ndarray:
    """Resets the state of the environment and returns an initial observation.

    Returns:
      The initial observation for each agent, with shape (n_agents, n_senses). See :ref:`senses`

    Raises:
      ConnectionLostError: If there was a connection error in battle mode
    """
    return asyncio.get_event_loop().run_until_complete(self.async_reset())

  def step(self, action_n: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray, List[bool], List[Dict]]:
    """Run one timestep.

    Accepts a list of actions, one for each agent, and returns the current state.

    Actions can have one of the following formats/shapes:

    * Numpy array of shape (:attr:`n_teams`, :attr:`n_agents_per_team`, :attr:`n_actions`)
    * Numpy array of shape (:attr:`n_agents`, :attr:`n_actions`)
    * List of actions (i.e. ``[[1, 0, 0, 2, 0], [0, 1, 0, 0, 3], ...]``), one inner array per agent. This is just cast to a numpy array of shape (:attr:`n_agents`, :attr:`n_actions`).

    The returned observations are laid out in the same way as the actions, and can therefore
    be reshape like the above. For instance: ``observations.reshape((env.n_teams, env.n_agents_per_team, -1))``

    Args:
      action_n: Numpy array or list of actions. See :ref:`actions`

    Returns:
      A tuple of (observation_n, reward_n, done_n, info). See :ref:`senses`.
      observation_n has shape (n_agents, n_senses)

    Raises:
      ConnectionLostError: If there was a connection error in connected mode
    """
    return asyncio.get_event_loop().run_until_complete(self.async_step(action_n))

  def close(self):
    """Shut down environment
    """
    return asyncio.get_event_loop().run_until_complete(self.async_close())

  async def async_init_browser(self):
    """Creates a browser instance. This only needs to be invoked if no_init_browser was passed to the constructor"""
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
    self.logger.info('[init] Getting sense count')
    self.n_senses = await self.page.evaluate('''() => window.derk.nSenses''')
    self.logger.info('[init] Connecting to environments')
    await self._connect_environments()
    self.logger.info('[init] Done!')

  async def _connect_environments(self):
    envs = ENVS_DUAL_LOCAL if self.mode == 'connected' else ENVS_SINGLE_LOCAL
    await self.page.evaluate('''(envs, nArenas, inWorker) => window.derk.connectToEnvironments(envs, nArenas, inWorker)''', envs, self.n_arenas, self.web_socket_worker)

  def _handle_console(self, m):
    if m.type == 'error':
      self.logger.error('[console] %s', m.text)
    elif m.type == 'warning':
      self.logger.warning('[console] %s', m.text)
    else:
      self.logger.info('[console] %s', m.text)

  async def _handle_websocket(self, websocket, path):
    self.logger.info('[_handle_websocket] Got websocket connection')
    remote_connection = self.remote_connection
    remote_messages = self.remote_messages
    self.n_teams = json.loads(await websocket.recv())['nTeams']
    remote_connection.set_result(websocket)
    try:
      async for message in websocket:
        await remote_messages.put(message)
    except websockets.exceptions.ConnectionClosedError:
      self.logger.info('[_handle_websocket] Connection lost')
    self.remote_connection = asyncio.Future()
    self.remote_messages = asyncio.Queue()
    await remote_messages.put('connection_ended')
    self.logger.info('[_handle_websocket] Websocket disconnected')

  async def async_reset(self):
    """Async version of :meth:`reset`"""
    self.logger.info('[reset] Resetting...')
    if self.dummy_mode:
      return [self.observation_space.sample() for i in range(self.n_agents)]
    if self.page:
      if self.running_episode:
        await self.running_episode
      if self.safe_reset:
        self.logger.info('[reset] Running safe reset (reload page)')
        await self.page.reload()
        self.logger.info('[reset] Waiting for GymLoaded')
        await self.page.waitForSelector('.GymLoaded')
        self.logger.info('[reset] Gym loaded ok')
        await self._connect_environments()
      config = {
        'home': self.home_team,
        'away': self.away_team,
        'rewardFunction': self.reward_function,
        'nArenas': self.n_arenas,
        'substeps': self.substeps,
        'turboMode': self.turbo_mode,
        'interleaved': self.interleaved,
        'debugNoObservations': self.debug_no_observations,
      }
      self.running_episode = asyncio.get_event_loop().create_task(self.page.evaluate('''(config) => window.derk.runEpisode(config)''', config))

    self.total_reward = np.zeros((self.n_agents))
    self.logger.info('[reset] Waiting for observations')
    observations = self._decode_observations(await self._get_msg())
    self.logger.info('[reset] Got observations')
    return observations

  async def _get_msg(self):
    msg = await self.remote_messages.get()
    if msg == "connection_ended":
      raise ConnectionLostError(self)
    return msg

  async def async_close(self):
    """Async version of :meth:`close`"""
    self.logger.info('[async_close] Closing environment')
    self.websocket_server.close()
    if self.running_episode:
      try:
        await self.running_episode
      except Exception as err:
        print('Running episode raised error', err)
    if self.browser:
      await self.browser.close()
    if self.internal_http_server:
      self.bundle_server.shutdown()
    self.logger.info('[async_close] Done')

  async def async_step(self, action_n: np.ndarray):
    """Async version of :meth:`step`"""
    if self.dummy_mode:
      return (
        [self.observation_space.sample() for i in range(self.n_agents)],
        [random() for i in range(self.n_agents)],
        [False for i in range(self.n_agents)],
        [{} for i in range(self.n_agents)],
      )

    try:
      websocket = self.remote_connection.result()
    except asyncio.InvalidStateError:
      raise ConnectionLostError(self)
    actions_arr = np.asarray(action_n, dtype='float32').reshape((-1)).tobytes()
    try:
      await websocket.send(actions_arr)
    except websockets.exceptions.ConnectionClosedError:
      raise ConnectionLostError(self)

    observations = self._decode_observations(await self._get_msg())
    reward = self._decode_reward(await self._get_msg())
    res = json.loads(await self._get_msg())

    self.total_reward = np.add(self.total_reward, reward)
    if 'roundStats' in res:
      self.episode_stats = res['roundStats']

    return observations, reward, res['done'], None

  def get_webgl_renderer(self) -> str:
    """Return which webgl renderer is being used by the game"""
    return asyncio.get_event_loop().run_until_complete(self.async_get_webgl_renderer())

  async def async_get_webgl_renderer(self):
    """Async version of :meth:`get_webgl_renderer`"""
    return await self.page.evaluate('''() => window.derk.getWebGLRenderer()''')

  def _decode_observations(self, observations):
    obs = np.frombuffer(observations, dtype='float32')
    # Images/textures in WebGL are layed out in layer for z, and 4 components per channel
    return obs.reshape((int(self.n_senses / 4), -1, 4)).swapaxes(0, 1).reshape((-1, self.n_senses))

  def _decode_reward(self, reward):
    return np.frombuffer(reward, dtype='float32')
