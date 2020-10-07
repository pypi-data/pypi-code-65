#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpRigToolkit-tools-interpolateit client implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from tpDcc.core import client


class InterpolateItClient(client.DccClient, object):

    PORT = 18231

    # =================================================================================================================
    # BASE
    # =================================================================================================================

    def get_attributes_data_to_store(self, node, transform_attributes=True, user_attributes=False):
        cmd = {
            'cmd': 'get_attributes_data_to_store',
            'node': node,
            'transform_attributes': transform_attributes,
            'user_attributes': user_attributes
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['result']

    def reset_attributes(self, node, attributes_dict):
        cmd = {
            'cmd': 'reset_attributes',
            'node': node,
            'attributes_dict': attributes_dict
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['success']

    def set_stored_attribute_value(self, node, attribute_name, attribute_value):
        cmd = {
            'cmd': 'set_stored_attribute_value',
            'node': node,
            'attribute_name': attribute_name,
            'attribute_value': attribute_value
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return list()

        return reply_dict['success']
