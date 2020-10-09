# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import time
import os
from .constants import (STATE_WAITING, STATE_SYNCING, STATE_AUTH,
                        STATE_CONFIG, STATE_ACTIVE, STATE_SRV_SYNC,
                        STATE_INITIAL, STATE_QUITTING,
                        STATE_LAUNCHING_SERVICES, STATE_LOBBY)
try:
    import psutil
    print('psutil available')
    psutil_available = True
except ImportError:
    psutil_available = False


def current_milli_time():
    """ Retrieve current time in millisecond """
    return int(round(time.time() * 1000))


def assert_parent_process_running():
    """ 
        Check if the parent process is alive, 
        if not it kill the child
    """
    if psutil_available:
        try:
            psutil.Process(os.getppid())
        except psutil.NoSuchProcess:
            p = psutil.Process(os.getpid())
            p.kill()


def get_state_str(state):
    state_str = 'UNKOWN'
    if state == STATE_WAITING:
        state_str = 'WARMING UP DATA'
    elif state == STATE_SYNCING:
        state_str = 'FETCHING'
    elif state == STATE_AUTH:
        state_str = 'AUTHENTICATION'
    elif state == STATE_CONFIG:
        state_str = 'CONFIGURATION'
    elif state == STATE_ACTIVE:
        state_str = 'ONLINE'
    elif state == STATE_SRV_SYNC:
        state_str = 'PUSHING'
    elif state == STATE_INITIAL:
        state_str = 'OFFLINE'
    elif state == STATE_QUITTING:
        state_str = 'QUITTING'
    elif state == STATE_LAUNCHING_SERVICES:
        state_str = 'LAUNCHING SERVICES'
    elif state == STATE_LOBBY:
        state_str = 'LOBBY'

    return state_str
