import json
import re

import requests

from sdcclient._common import _SdcCommon
from sdcclient.monitor import EventsClientV2, DashboardsClientV3


class SdMonitorClient(DashboardsClientV3, EventsClientV2, _SdcCommon):

    def __init__(self, token="", sdc_url='https://app.sysdigcloud.com', ssl_verify=True, custom_headers=None):
        super(SdMonitorClient, self).__init__(token, sdc_url, ssl_verify, custom_headers)
        self.product = "SDC"


    def get_alerts(self):
        '''**Description**
            Retrieve the list of alerts configured by the user.

        **Success Return Value**
            An array of alert dictionaries, with the format described at `this link <https://app.sysdigcloud.com/apidocs/#!/Alerts/get_api_alerts>`__

        **Example**
            `examples/list_alerts.py <https://github.com/draios/python-sdc-client/blob/master/examples/list_alerts.py>`_
        '''
        res = requests.get(self.url + '/api/alerts', headers=self.hdrs, verify=self.ssl_verify)
        return self._request_result(res)

    def get_notifications(self, from_ts, to_ts, state=None, resolved=None):
        '''**Description**
            Returns the list of Sysdig Monitor alert notifications.

        **Arguments**
            - **from_ts**: filter events by start time. Timestamp format is in UTC (seconds).
            - **to_ts**: filter events by start time. Timestamp format is in UTC (seconds).
            - **state**: filter events by alert state. Supported values are ``OK`` and ``ACTIVE``.
            - **resolved**: filter events by resolution status. Supported values are ``True`` and ``False``.

        **Success Return Value**
            A dictionary containing the list of notifications.

        **Example**
            `examples/list_alert_notifications.py <https://github.com/draios/python-sdc-client/blob/master/examples/list_alert_notifications.py>`_
        '''
        params = {}

        if from_ts is not None:
            params['from'] = from_ts * 1000000

        if to_ts is not None:
            params['to'] = to_ts * 1000000

        if state is not None:
            params['state'] = state

        if resolved is not None:
            params['resolved'] = resolved

        res = requests.get(self.url + '/api/notifications', headers=self.hdrs, params=params, verify=self.ssl_verify)
        if not self._checkResponse(res):
            return [False, self.lasterr]
        return [True, res.json()]

    def update_notification_resolution(self, notification, resolved):
        '''**Description**
            Updates the resolution status of an alert notification.

        **Arguments**
            - **notification**: notification object as returned by :func:`~SdcClient.get_notifications`.
            - **resolved**: new resolution status. Supported values are ``True`` and ``False``.

        **Success Return Value**
            The updated notification.

        **Example**
            `examples/resolve_alert_notifications.py <https://github.com/draios/python-sdc-client/blob/master/examples/resolve_alert_notifications.py>`_
        '''
        if 'id' not in notification:
            return [False, 'Invalid notification format']

        notification['resolved'] = resolved
        data = {'notification': notification}

        res = requests.put(self.url + '/api/notifications/' + str(notification['id']), headers=self.hdrs, data=json.dumps(data), verify=self.ssl_verify)
        return self._request_result(res)

    def create_alert(self, name=None, description=None, severity=None, for_atleast_s=None, condition=None,
                     segmentby=None, segment_condition='ANY', user_filter='', notify=None, enabled=True,
                     annotations=None, alert_obj=None, type="MANUAL"):
        '''**Description**
            Create a threshold-based alert.

        **Arguments**
            - **name**: the alert name. This will appear in the Sysdig Monitor UI and in notification emails.
            - **description**: the alert description. This will appear in the Sysdig Monitor UI and in notification emails.
            - **severity**: syslog-encoded alert severity. This is a number from 0 to 7 where 0 means 'emergency' and 7 is 'debug'.
            - **for_atleast_s**: the number of consecutive seconds the condition must be satisfied for the alert to fire.
            - **condition**: the alert condition, as described here https://app.sysdigcloud.com/apidocs/#!/Alerts/post_api_alerts
            - **segmentby**: a list of Sysdig Monitor segmentation criteria that can be used to apply the alert to multiple entities. For example, segmenting a CPU alert by ['host.mac', 'proc.name'] allows to apply it to any process in any machine.
            - **segment_condition**: When *segmentby* is specified (and therefore the alert will cover multiple entities) this field is used to determine when it will fire. In particular, you have two options for *segment_condition*: **ANY** (the alert will fire when at least one of the monitored entities satisfies the condition) and **ALL** (the alert will fire when all of the monitored entities satisfy the condition).
            - **user_filter**: a boolean expression combining Sysdig Monitor segmentation criteria that makes it possible to reduce the scope of the alert. For example: *kubernetes.namespace.name='production' and container.image='nginx'*.
            - **notify**: the type of notification you want this alert to generate. Options are *EMAIL*, *SNS*, *PAGER_DUTY*, *SYSDIG_DUMP*.
            - **enabled**: if True, the alert will be enabled when created.
            - **annotations**: an optional dictionary of custom properties that you can associate to this alert for automation or management reasons
            - **alert_obj**: an optional fully-formed Alert object of the format returned in an "alerts" list by :func:`~SdcClient.get_alerts` This is an alternative to creating the Alert using the individual parameters listed above.

        **Success Return Value**
            A dictionary describing the just created alert, with the format described at `this link <https://app.sysdigcloud.com/apidocs/#!/Alerts/post_api_alerts>`__

        **Example**
            `examples/create_alert.py <https://github.com/draios/python-sdc-client/blob/master/examples/create_alert.py>`_
        '''

        if annotations is None:
            annotations = {}

        if segmentby is None:
            segmentby = []

        #
        # Get the list of alerts from the server
        #
        res = requests.get(self.url + '/api/alerts', headers=self.hdrs, verify=self.ssl_verify)
        if not self._checkResponse(res):
            return [False, self.lasterr]
        res.json()

        if alert_obj is None:
            if None in (name, description, severity, for_atleast_s, condition):
                return [False, 'Must specify a full Alert object or all parameters: name, description, severity, for_atleast_s, condition']
            else:
                #
                # Populate the alert information
                #
                alert_json = {
                    'alert': {
                        'type': type,
                        'name': name,
                        'description': description,
                        'enabled': enabled,
                        'severity': severity,
                        'timespan': for_atleast_s * 1000000,
                        'condition': condition,
                        'filter': user_filter
                    }
                }

                if segmentby != None and segmentby != []:
                    alert_json['alert']['segmentBy'] = segmentby
                    alert_json['alert']['segmentCondition'] = {'type': segment_condition}

                if annotations != None and annotations != {}:
                    alert_json['alert']['annotations'] = annotations

                if notify != None:
                    alert_json['alert']['notificationChannelIds'] = notify
        else:
            # The REST API enforces "Alert ID and version must be null", so remove them if present,
            # since these would have been there in a dump from the list_alerts.py example.
            alert_obj.pop('id', None)
            alert_obj.pop('version', None)
            alert_json = {
                'alert': alert_obj
            }

        #
        # Create the new alert
        #
        res = requests.post(self.url + '/api/alerts', headers=self.hdrs, data=json.dumps(alert_json), verify=self.ssl_verify)
        return self._request_result(res)

    def update_alert(self, alert):
        '''**Description**
            Update a modified threshold-based alert.

        **Arguments**
            - **alert**: one modified alert object of the same format as those in the list returned by :func:`~SdcClient.get_alerts`.

        **Success Return Value**
            The updated alert.

        **Example**
            `examples/update_alert.py <https://github.com/draios/python-sdc-client/blob/master/examples/update_alert.py>`_
        '''
        if 'id' not in alert:
            return [False, "Invalid alert format"]

        res = requests.put(self.url + '/api/alerts/' + str(alert['id']), headers=self.hdrs, data=json.dumps({"alert": alert}), verify=self.ssl_verify)
        return self._request_result(res)

    def delete_alert(self, alert):
        '''**Description**
            Deletes an alert.

        **Arguments**
            - **alert**: the alert dictionary as returned by :func:`~SdcClient.get_alerts`.

        **Success Return Value**
            ``None``.

        **Example**
            `examples/delete_alert.py <https://github.com/draios/python-sdc-client/blob/master/examples/delete_alert.py>`_
        '''
        if 'id' not in alert:
            return [False, 'Invalid alert format']

        res = requests.delete(self.url + '/api/alerts/' + str(alert['id']), headers=self.hdrs, verify=self.ssl_verify)
        if not self._checkResponse(res):
            return [False, self.lasterr]

        return [True, None]

    def get_explore_grouping_hierarchy(self):
        '''**Description**
            Return the user's current grouping hierarchy as visible in the Explore tab of Sysdig Monitor.

        **Success Return Value**
            A list containing the list of the user's Explore grouping criteria.

        **Example**
            `examples/print_explore_grouping.py <https://github.com/draios/python-sdc-client/blob/master/examples/print_explore_grouping.py>`_
        '''
        res = requests.get(self.url + '/api/groupConfigurations', headers=self.hdrs, verify=self.ssl_verify)
        if not self._checkResponse(res):
            return [False, self.lasterr]

        data = res.json()

        if 'groupConfigurations' not in data:
            return [False, 'corrupted groupConfigurations API response']

        gconfs = data['groupConfigurations']

        for gconf in gconfs:
            if gconf['id'] == 'explore':
                res = []
                items = gconf['groups'][0]['groupBy']

                for item in items:
                    res.append(item['metric'])

                return [True, res]

        return [False, 'corrupted groupConfigurations API response, missing "explore" entry']

    def set_explore_grouping_hierarchy(self, new_hierarchy):
        '''**Description**
            Changes the grouping hierarchy in the Explore panel of the current user.

        **Arguments**
            - **new_hierarchy**: a list of sysdig segmentation metrics indicating the new grouping hierarchy.
        '''
        body = {
            'id': 'explore',
            'groups': [{'groupBy': []}]
        }

        for item in new_hierarchy:
            body['groups'][0]['groupBy'].append({'metric': item})

        res = requests.put(self.url + '/api/groupConfigurations/explore', headers=self.hdrs,
                           data=json.dumps(body), verify=self.ssl_verify)
        if not self._checkResponse(res):
            return [False, self.lasterr]
        else:
            return [True, None]


    def get_metrics(self):
        '''**Description**
            Return the metric list that can be used for data requests/alerts/dashboards.

        **Success Return Value**
            A dictionary containing the list of available metrics.

        **Example**
            `examples/list_metrics.py <https://github.com/draios/python-sdc-client/blob/master/examples/list_metrics.py>`_
        '''
        res = requests.get(self.url + '/api/data/metrics', headers=self.hdrs, verify=self.ssl_verify)
        return self._request_result(res)

    @staticmethod
    def convert_scope_string_to_expression(scope):
        '''**Description**
            Internal function to convert a filter string to a filter object to be used with dashboards.
        '''
        #
        # NOTE: The supported grammar is not perfectly aligned with the grammar supported by the Sysdig backend.
        # Proper grammar implementation will happen soon.
        # For practical purposes, the parsing will have equivalent results.
        #

        if scope is None or not scope:
            return [True, []]

        expressions = []
        string_expressions = scope.strip(' \t\n\r').split(' and ')
        expression_re = re.compile('^(?P<not>not )?(?P<operand>[^ ]+) (?P<operator>=|!=|in|contains|starts with) (?P<value>(:?"[^"]+"|\'[^\']+\'|\(.+\)|.+))$')

        for string_expression in string_expressions:
            matches = expression_re.match(string_expression)

            if matches is None:
                return [False, 'invalid scope format']

            is_not_operator = matches.group('not') is not None

            if matches.group('operator') == 'in':
                list_value = matches.group('value').strip(' ()')
                value_matches = re.findall('(:?\'[^\',]+\')|(:?"[^",]+")|(:?[,]+)', list_value)

                if len(value_matches) == 0:
                    return [False, 'invalid scope value list format']

                value_matches = map(lambda v: v[0] if v[0] else v[1], value_matches)
                values = map(lambda v: v.strip(' "\''), value_matches)
            else:
                values = [matches.group('value').strip('"\'')]

            operator_parse_dict = {
                'in': 'in' if not is_not_operator else 'notIn',
                '=': 'equals' if not is_not_operator else 'notEquals',
                '!=': 'notEquals' if not is_not_operator else 'equals',
                'contains': 'contains' if not is_not_operator else 'notContains',
                'starts with': 'startsWith'
            }

            operator = operator_parse_dict.get(matches.group('operator'), None)
            if operator is None:
                return [False, 'invalid scope operator']

            expressions.append({
                'operand': matches.group('operand'),
                'operator': operator,
                'value': values
            })

        return [True, expressions]


# For backwards compatibility
SdcClient = SdMonitorClient
