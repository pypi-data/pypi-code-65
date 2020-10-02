from __future__ import print_function

__author__ = 'saeedamen'  # Saeed Amen / saeed@cuemacro.com

#
# Copyright 2017 Cuemacro Ltd. - http//www.cuemacro.com / @cuemacro
#
# See the License for the specific language governing permissions and limitations under the License.
#

from findatapy.util.singleton import Singleton

import threading

class Mediator(object):
    """Mediator acts as a source for static/one off objects such as the VolatileCache, TCAMarketTradeLoader,
    TCATickerLoader etc.  Also allows users to create their own subclasses of these and distribute universally to the
    project, without having to worry about importing the appropriate classes/implementations.

    """
    __metaclass__ = Singleton

    _data_constants = None
    _data_constants_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def get_data_constants():
        with Mediator._data_constants_lock():

            from findatapy.util.dataconstants import DataConstants

            Mediator._data_constants = DataConstants()

        return Mediator._data_constants


