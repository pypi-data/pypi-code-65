#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigToolkit-tools-interpolateit server implementation for 3ds Max
"""

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from pymxs import runtime as rt

import tpDcc as tp
from tpDcc.core import server

LOGGER = tp.LogsMgr().get_logger('tpRigToolkit-tools-interpolateit')


class InterpolateItServer(server.DccServer, object):

    PORT = 18231

    def _process_command(self, command_name, data_dict, reply_dict):
        if command_name == 'get_attributes_data_to_store':
            self.get_attributes_data_to_store(data_dict, reply_dict)
        elif command_name == 'reset_attributes':
            self.reset_attributes(data_dict, reply_dict)
        elif command_name == 'set_stored_attribute_value':
            self.set_stored_attribute_value(data_dict, reply_dict)
        else:
            super(InterpolateItServer, self)._process_command(command_name, data_dict, reply_dict)

    def get_attributes_data_to_store(self, data, reply):
        node = data['node']
        transform_attributes = data['transform_attributes']
        user_attributes = data['user_attributes']
        if not node:
            reply['msg'] = 'No note given to retrieve attributes to store of'
            reply['success'] = False
            return

        attributes_data = dict()

        if transform_attributes:
            xform_attribute_names = [tp.Dcc.TRANSLATION_ATTR_NAME, tp.Dcc.ROTATION_ATTR_NAME, tp.Dcc.SCALE_ATTR_NAME]
            for xform in xform_attribute_names:
                xform_value = tp.Dcc.get_attribute_value(node, xform)
                if xform == tp.Dcc.ROTATION_ATTR_NAME:
                    rotation_as_euler = rt.quatToEuler(xform_value)
                    xform_value = [rotation_as_euler.x, rotation_as_euler.y, rotation_as_euler.z]
                else:
                    xform_value = list(xform_value)
                for i, axis in enumerate(tp.Dcc.AXES):
                    channel = '{}{}'.format(xform, axis.upper())
                    attributes_data[channel] = xform_value[i]
                    if tp.Dcc.is_attribute_locked(node, channel):
                        attributes_data[channel][i] = None

        if user_attributes:
            pass

        reply['result'] = attributes_data
        reply['success'] = True

    @tp.Dcc.undo_decorator()
    def reset_attributes(self, data, reply):
        # TODO: Add support for reset attributes
        # NOTE: In Max, we need to store extra data attribute when saving start values (store default values)
        reply['success'] = True

    def set_stored_attribute_value(self, data, reply):
        node = data['node']
        attribute_name = data['attribute_name']
        attribute_value = data['attribute_value']

        tp.Dcc.set_attribute_value(node, attribute_name, attribute_value)
        tp.Dcc.refresh_viewport()

        reply['success'] = True
