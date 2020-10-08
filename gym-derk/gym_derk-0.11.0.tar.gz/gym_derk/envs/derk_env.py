import gym
import asyncio
import os
from typing import List, Dict, Tuple
import numpy as np
from gym_derk.derk_app_instance import DerkAppInstance
from gym_derk.derk_server import DerkAgentServer, DerkSession
import logging

logger = logging.getLogger(__name__)

class DerkEnv(gym.Env):
  """Reinforcement Learning environment for "Dr. Derk's Mutant Battlegrounds"

  There are two modes for the environment:

  * ``mode="normal"``: You control both the home and away teams.
  * ``mode="connected"``: Connects this environment to another agent. See :ref:`connected_mode`.

  Args:
    mode: ``"normal"`` (default), ``"connected"``. See above for details. (Environment variable: DERK_MODE)
    session_args: See arguments to :meth:`gym_derk.DerkAppInstance.create_session`
    app_args: See arguments to :class:`gym_derk.DerkAppInstance`
    agent_server_args: See arguments to :class:`gym_derk.DerkAgentServer`

  This is a convenience wrapper of the more low level api of :class:`gym_derk.DerkAppInstance`,
  :class:`gym_derk.DerkAgentServer` and :class:`gym_derk.DerkSession`.

  """
  def __init__(self, mode: str=False, session_args: Dict={}, app_args: Dict={}, agent_server_args: Dict={}):

    self.mode = mode if mode is not None else os.environ.get('DERK_MODE', 'normal')
    self.session_args = session_args

    self.session = asyncio.Future()
    if 'port' not in agent_server_args:
      agent_server_args['port'] = 8788
    self.logger = logger.getChild('DerkEnv({})'.format(agent_server_args['port']))
    self.server = DerkAgentServer(self._handle_session, **agent_server_args)
    asyncio.get_event_loop().run_until_complete(self.server.start())

    if 'agent_hosts' not in self.session_args:
      if self.mode == 'connected':
        self.session_args['agent_hosts'] = [{ 'uri': self.server.uri, 'regions': [{ 'sides': 'home' }] }, { 'uri': 'ws://127.0.0.1:8789', 'regions': [{ 'sides': 'away' }] }]
      else:
        self.session_args['agent_hosts'] = [{ 'uri': self.server.uri, 'regions': [{ 'sides': 'both' }] }]

    self.instance = DerkAppInstance(**app_args)

    asyncio.get_event_loop().run_until_complete(self.instance.create_session(**self.session_args))
    self.can_reset = True

    asyncio.get_event_loop().run_until_complete(self.session)
    self.running_session = asyncio.get_event_loop().create_task(self.instance.run_episodes_loop())

  @property
  def n_agents(self):
    """Number of agents controlled by this environment

    I.e. ``env.n_teams * env.n_agents_per_team``
    """
    return self.session.result().n_agents

  @property
  def n_teams(self):
    """Number of teams controlled by this environment"""
    return self.session.result().n_teams

  @property
  def n_agents_per_team(self):
    """Number of agents in a team (3)"""
    return self.session.result().n_agents_per_team

  @property
  def action_keys(self):
    """Enum with all action outputs (len=5)"""
    return self.session.result().action_keys

  @property
  def observation_keys(self):
    """Enum with all observation outputs"""
    return self.session.result().observation_keys

  @property
  def action_space(self):
    """Gym space for actions"""
    return self.session.result().action_space

  @property
  def observation_space(self):
    """Gym space for observations"""
    return self.session.result().observation_space

  @property
  def total_reward(self):
    """Accumulated rewards over an episode"""
    return self.session.result().total_reward

  @property
  def episode_stats(self):
    """Stats for the last episode"""
    return self.session.result().episode_stats

  def reset(self) -> np.ndarray:
    """Resets the state of the environment and returns an initial observation.

    Returns:
      The initial observation for each agent, with shape (n_agents, len(observation_keys)). See :ref:`senses`

    Raises:
      ConnectionLostError: If there was a connection error in connected mode
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
      observation_n has shape (n_agents, len(observation_keys))

    Raises:
      ConnectionLostError: If there was a connection error in connected mode
    """
    return asyncio.get_event_loop().run_until_complete(self.async_step(action_n))

  def close(self):
    """Shut down environment
    """
    return asyncio.get_event_loop().run_until_complete(self.async_close())

  async def _handle_session(self, session):
    self.logger.info('[_handle_session] Got session')
    self.session.set_result(session)
    await session.websocket.wait_closed()

  async def async_close(self):
    """Async version of :meth:`close`"""
    self.logger.info('[async_close] Closing environment')
    self.server.close()
    await self.instance.close()
    await self.running_session
    self.logger.info('[async_close] Done')

  async def async_reset(self):
    """Async version of :meth:`reset`"""
    if not self.can_reset:
      await self.session.result().close()
      await self.running_session
      self.session = asyncio.Future()
      await self.instance.create_session(**self.session_args)
      self.running_session = asyncio.get_event_loop().create_task(self.instance.run_episodes_loop())
    return await (await self.session).reset()

  async def async_step(self, action_n: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray, List[bool], List[Dict]]:
    """Async version of :meth:`step`"""
    res = await (await self.session).step(action_n)
    self.can_reset = all(res[2])
    return res
