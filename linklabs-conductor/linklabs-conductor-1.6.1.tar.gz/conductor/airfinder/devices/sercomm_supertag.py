from conductor.airfinder.devices.supertag import Supertag, SupertagDownlinkMessageSpecV2


class SercommDownlinkMessageSpecV2_0(SupertagDownlinkMessageSpecV2):
    """ Sercomm Message Spec V2.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x01]})

        # Remove Ack from Message Spec.
        self.msg_types.pop('Ack')

        # Update new message types
        #   - Update Configuration
        #       + Removed Shock Threshold
        #       + Added Sym Retries
        #       + Added Network Token
        #   - Added Battery Consumption Window
        #   - Added Setting Diagnostic Mode
        #   - Added Requesting Consumption
        #   - Added Setting Throttling
        #   - Added FTP Information
        self.msg_types.update({
            'Configuration': {
                'def': ['mask', 'heartbeat', 'no_ap_heartbeat', 'no_sym_heartbeat', 'location_update_rate',
                        'no_ap_location_update_rate', 'no_sym_location_update_rate', 'transition_base_update_rate',
                        'transition_increasing_interval_enable', 'scans_per_fix', 'max_wifi_aps', 'max_cell_ids',
                        'location_update_order', 'acc_enable', 'acc_duration', 'acc_threshold', 'cache_enable',
                        'cache_length', 'gps_power_mode', 'gps_timeout', 'network_lost_timeout', 'ref_lost_timeout',
                        'network_scan_interval', 'sym_retries', 'network_token'],
                'struct': '>IIIIIIIIBBBBBBHHBBBHHHHBI',
                'defaults': [0x00000000, 0x0000003c, 0x00015180, 0x00015180, 0x0000000b, 0x0000003c, 0x00005460,
                             0x0000000b, 0x00, 0x04, 0x0a, 0x00, 0x1b, 0x01, 0x0003, 0x0050, 0x00, 0x00, 0x00, 0x00b4,
                             0x0258, 0x0258, 0x00b4, 0x05, 0x4f50454e]
            },
            'BattConsumptionWindow': {
                'def': ['mask', 'battery_capacity', 'start_up_power', 'alive_time_power', 'location_update_power',
                        'network_scan_power', 'ble_connection_power', 'lte_success_power', 'lte_failed_power',
                        'gps_avg_power', 'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power',
                        'ftp_power'],
                'struct': '>IIIIHHHIIIIHHII',
                'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x0000, 0x00000000,
                             0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x00000000, 0x00000000]
            },
            'SetDiagnosticMode': {
                'def': ['enable'],
                'struct': '>B',
                'defaults': [0x00]
            },
            'ConsumptionRequest': {},
            'SetThrottling': {
                'def': ['mask', 'enable', 'mode', 'win_len', 'min_batt', 'win_limit', 'batt_cap'],
                'struct': '>HBBIIBI',
                'defaults': [0x00, 0x00, 0x01, 0x0000001e, 0x00011940, 0x5a, 0x01010100]
            },
            'FtpAvailable': {
                'def': ['app_vers_major', 'app_vers_minor', 'app_vers_tag', 'modem_vers_major', 'modem_vers_minor',
                        'modem_vers_tag'],
                'struct': '>BBHBBH',
                'defaults': [0x00, 0x00, 0x0000, 0x00, 0x00, 0x0000]
            }
        })


class SercommDownlinkMessageSpecV2_1(SercommDownlinkMessageSpecV2_0):
    """ Sercomm Message Spec V2.1.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x02]})

        # Update new message types
        #   - Update Configuration
        #       + Added Transition Base Update
        #       + Added Transition Increasing Int En
        #   - Added CoAP Server Downlink
        #   - Update Battery Consumption
        #       + Shipping Mode Power
        #       + PSM Sleep Power
        self.msg_types.update({
            'BattConsumptionWindow': {
                'def': ['mask', 'battery_capacity', 'shipping_mode_power', 'start_up_power', 'alive_time_power',
                        'psm_sleep_power', 'location_update_power', 'network_scan_power', 'ble_connection_power',
                        'lte_success_power', 'lte_failed_power', 'lte_registration_power', 'gps_avg_power',
                        'wifi_avg_power', 'temp_read_power', 'battery_read_power', 'led_power', 'ftp_power'],
                'struct': '>IIIIIHHHIIIIHHII',
                'defaults': [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x0000, 0x00000000,
                             0x00000000, 0x00000000, 0x00000000, 0x0000, 0x0000, 0x00000000, 0x00000000]
            },
        })


class SercommDownlinkMessageSpecV2_2(SercommDownlinkMessageSpecV2_1):
    """ Sercomm Message Spec V2.0.0. """

    def __init__(self):
        super().__init__()

        # Update Message Spec Version
        self.header.update({'defaults': [0x00, 0x02]})


class SercommSupertag(Supertag):
    """ """

    application = "d29b3be8f2cc9a1a7051"

    @property
    def symble_version(self):
        raise NotImplementedError()

    @property
    def hw_id(self):
        return self._make_prop(str, "hwId")

    @property
    def heartbeat(self):
        return self._make_prop(int, "heartbeatInterval")

    @property
    def no_ap_heartbeat(self):
        return self._make_prop(int, "noApHeartbeatInterval")

    @property
    def no_sym_heartbeat(self):
        return self._make_prop(int, "noSymHeartbeatInterval")

    @property
    def location_update_rate(self):
        return self._make_prop(int, "locationUpdateRate")

    @property
    def no_ap_location_update_rate(self):
        return self._make_prop(int, "noApLocationUpdateRate")

    @property
    def no_sym_location_update_rate(self):
        return self._make_prop(int, "noSymLocationUpdateRate")

    @property
    def transition_base_update_rate(self):
        return self._make_prop(int, "transitionBaseInterval")

    @property
    def transition_increasing_interval_enable(self):
        return self._make_prop(bool, "transitionIntervalEnable")

    @property
    def scans_per_fix(self):
        return self._make_prop(int, "scansPerFix")

    @property
    def max_wifi_aps(self):
        return self._make_prop(int, "maxWifis")

    @property
    def max_cell_ids(self):
        return self._make_prop(int, "maxCellIds")

    @property
    def location_update_order(self):
        return self._make_prop(int, "locationUpdateOrder")

    @property
    def acc_enable(self):
        return self._make_prop(int, "accelerometerEnable")

    @property
    def acc_duration(self):
        return self._make_prop(int, "accelerometerMovementDuration")

    @property
    def acc_threshold(self):
        return self._make_prop(int, "accelerometerThreshold")

    @property
    def cache_enable(self):
        return self._make_prop(int, "cachedMessagesEnable")

    @property
    def cache_length(self):
        return self._make_prop(int, "noSymMessagesCached")

    @property
    def gps_power_mode(self):
        return self._make_prop(str, "gpsPowerMode")

    @property
    def gps_timeout(self):
        return self._make_prop(int, "gpsTimeout")

    @property
    def network_lost_timeout(self):
        return self._make_prop(int, "networkLostTimeout")

    @property
    def ref_lost_timeout(self):
        return self._make_prop(int, "refLostTimeout")

    @property
    def network_scan_int(self):
        return self._make_prop(int, "networkScanInterval")

    @property
    def sym_retries(self):
        return self._make_prop(int, "symRetries")

    @property
    def network_token(self):
        return self._make_prop(int, "networkToken")

    @property
    def battery_capacity(self):
        return self._make_prop(int, "batteryCapacity_mAh")

    @property
    def start_up_power(self):
        return self._make_prop(int, "pwr-Boot_mAh")

    @property
    def alive_time_power(self):
        return self._make_prop(int, "avg_pwr-Alive_mAh")

    @property
    def location_update_power(self):
        return self._make_prop(int, "pwr-LocationScan_mAh")

    @property
    def network_scan_power(self):
        return self._make_prop(int, "pwr-NetworkScan_mAh")

    @property
    def ble_connection_power(self):
        return self._make_prop(int, "pwr-BleConnection_mAh")

    @property
    def lte_success_power(self):
        return self._make_prop(int, "pwr-LTEmSuccess_mAh")

    @property
    def lte_failed_power(self):
        return self._make_prop(int, "pwr-LTEmFailure_mAh")

    @property
    def gps_avg_power(self):
        return self._make_prop(int, "avg_pwr-ScanningGPS_mA")

    @property
    def wifi_avg_power(self):
        return self._make_prop(int, "avg_pwr-ScanningWIFI_mA")

    @property
    def temp_read_power(self):
        return self._make_prop(int, "pwr-TempReading_mAh")

    @property
    def battery_read_power(self):
        return self._make_prop(int, "pwr-BattReading_mAh")

    @property
    def led_power(self):
        return self._make_prop(int, "avg_pwr-LedOn_mA")

    @property
    def ftp_power(self):
        return self._make_prop(int, "pwr-LTEmFOTA_mAh")

    @classmethod
    def _get_spec(cls, vers):
        if vers.major == 1:
            return SercommDownlinkMessageSpecV2_0()
        elif vers.major == 2:
            return SercommDownlinkMessageSpecV2_2()
        else:
            raise Exception("No Supported Message Specification.")

    def set_batt_window(self, time_to_live_s=60.0, access_point=None, **kwargs):
        """ TODO """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("BattConsumptionWindow", **kwargs)
        return self._send_message(pld, time_to_live_s)

    @classmethod
    def multicast_set_batt_window(cls, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None, **kwargs):
        """ TODO """
        pld = cls._get_spec(vers).build_message("BattConsumptionWindow", **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, ap_vers, gws)

    def set_diag_mode(self, en, time_to_live_s=60.0, access_point=None):
        """ TODO """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("SetDiagnosticMode", enable=en)
        return self._send_message(pld, time_to_live_s)

    @classmethod
    def multicast_set_diag_mode(cls, en, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None):
        """ TODO """
        pld = cls._get_spec(vers).build_message("SetDiagnosticMode", enable=en)
        return cls._send_multicast_message(pld, time_to_live_s, ap_vers, gws)

    def req_batt_consumption(self, time_to_live_s=60.0, access_point=None):
        """ TODO: docs
        kwargs:
            'batt_cap', 'start_up_power', 'alive_time_power',
            'loc_upd_power', 'net_scan_power', 'ble_conn_power',
            'lte_success_power', 'lte_failed_power', 'gps_avg_power',
            'wifi_avg_power', 'temp_read_power', 'batt_read_power',
            'led_power', 'ftp_power'
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("ConsumptionRequest")
        return self._send_message(pld, time_to_live_s)

    @classmethod
    def multicast_req_batt_consumption(cls, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None):
        """ TODO """
        pld = cls._get_spec(vers).build_message("ConsumptionRequest")
        return cls._send_multicast_message(pld, time_to_live_s, ap_vers, gws)

    def set_throttling(self, time_to_live_s=60.0, access_point=None,
                       ap_vers=None, **kwargs):
        """ TODO: docs
        kwargs:
            'enable', 'mode', 'win_len', 'min_batt',
            'win_limit', 'batt_cap'
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("SetThrottling", **kwargs)
        return self._send_message(pld, time_to_live_s)

    @classmethod
    def multicast_set_throttling(cls, vers, gws, time_to_live_s=60.0,
                                 access_point=None, ap_vers=None, **kwargs):
        """ TODO  """
        pld = cls._get_spec(vers).build_message("SetThrottling", **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, ap_vers, gws)

    def ftp_notify(self, time_to_live_s=60.0, access_point=None, **kwargs):
        """ TODO: docs
        kwargs:
            'app_vers_major', 'app_vers_minor', 'app_vers_tag',
            'modem_vers_major', 'modem_vers_minor',
            'modem_vers_tag'
        """
        vers = self.msg_spec_version
        pld = self._get_spec(vers).build_message("FtpAvailable", **kwargs)
        return self._send_message(pld, time_to_live_s)

    @classmethod
    def multicast_ftp_notify(cls, vers, gws, time_to_live_s=60.0,
                             access_point=None, ap_vers=None, **kwargs):
        """ TODO """
        pld = cls._get_spec(vers).build_message("FtpAvailable", **kwargs)
        return cls._send_multicast_message(pld, time_to_live_s, ap_vers, gws)

    def ack(self, time_to_live_s=60.0, access_point=None):
        """ TODO """
        raise NotImplementedError

    @classmethod
    def multicast_ack(cls, vers, gws, time_to_live_s=60.0, access_point=None, ap_vers=None):
        """ TODO """
        raise NotImplementedError
