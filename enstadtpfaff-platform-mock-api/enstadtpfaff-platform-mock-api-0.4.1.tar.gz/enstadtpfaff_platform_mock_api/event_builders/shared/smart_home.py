import re
from enum import Enum
from typing import Optional

from enstadtpfaff_platform_mock_api.event import Event
from enstadtpfaff_platform_mock_api.util.topic_util import name_for_shared_topic


class Category(Enum):
    INDOOR_CLIMATE = "indoor-climate"
    LIGHTING = "lighting"
    RADIATION = "radiation"
    WINDOW = "window"
    UNIT_DOOR = "unit-door"
    BALCONY_DOOR = "balcony-door"
    ELECTRICITY = "electricity"
    PRESENCE = "presence"
    BLIND = "blind"
    GATE = "gate"
    SOCKET = "socket"
    MISC = "misc"
    MAILBOX = "mailbox"
    DOORBELL = "doorbell"


class ThermostatMode(Enum):
    OFF = 'OFF'
    ON = 'ON'
    HEAT = 'HEAT'
    COOL = 'COOL'
    AUTO = 'AUTO'


# noinspection PyPep8Naming
class IndoorClimate:
    def __init__(
            self,
            currentTemperature: Optional[float] = None,
            targetTemperature: Optional[float] = None,
            relativeHumidity: Optional[int] = None,
            pressure: Optional[float] = None,
            thermostatMode: Optional[ThermostatMode] = None,
            currentHeatingPower: Optional[float] = None,
            currentCoolingPower: Optional[float] = None
    ):
        self.currentTemperature = currentTemperature
        self.targetTemperature = targetTemperature
        self.relativeHumidity = relativeHumidity
        self.pressure = pressure
        self.thermostatMode = None if thermostatMode is None else thermostatMode.value
        self.currentHeatingPower = currentHeatingPower
        self.currentCoolingPower = currentCoolingPower


class OnOffState(Enum):
    OFF = "OFF"
    ON = "ON"


# noinspection PyPep8Naming
class Lighting:
    def __init__(
            self,
            dimmingLevel: Optional[int] = None,
            color: Optional[tuple] = None,
            colorTemperature: Optional[float] = None,
            state: Optional[OnOffState] = None
    ):
        if color is not None:
            if len(color) != 4:
                raise ValueError("invalid color")
            if color[0] < 0 or color[0] > 255:
                raise ValueError("invalid color")
            if color[1] < 0 or color[1] > 255:
                raise ValueError("invalid color")
            if color[2] < 0 or color[2] > 255:
                raise ValueError("invalid color")
            if color[3] < 0 or color[3] > 255:
                raise ValueError("invalid color")
        self.dimmingLevel = dimmingLevel
        self.color = color
        self.colorTemperature = colorTemperature
        self.state = None if state is None else state.value


# noinspection PyPep8Naming
class Radiation:
    def __init__(
            self,
            uvIndex: Optional[int] = None,
            brightness: Optional[float] = None
    ):
        self.uvIndex = uvIndex
        self.brightness = brightness


class OpeningState(Enum):
    LOCKED = "LOCKED"
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    TILTED = "TILTED"


# noinspection PyPep8Naming
class Window:
    def __init__(
            self,
            openingState: Optional[OpeningState] = None,
    ):
        self.openingState = None if openingState is None else openingState.value


# noinspection PyPep8Naming
class UnitDoor:
    def __init__(
            self,
            openingState: Optional[OpeningState] = None
    ):
        self.openingState = None if openingState is None else openingState.value


# noinspection PyPep8Naming
class BalconyDoor:
    def __init__(
            self,
            openingState: Optional[OpeningState] = None
    ):
        self.openingState = None if openingState is None else openingState.value


# noinspection PyPep8Naming
class Electricity:
    def __init__(
            self,
            currentPower: Optional[float] = None,
            current: Optional[float] = None,
            voltage: Optional[float] = None
    ):
        self.currentPower = currentPower
        self.current = current
        self.voltage = voltage


# noinspection PyPep8Naming
class Presence:
    def __init__(
            self,
            presenceDetected: Optional[bool] = None,
            presenceAmount: Optional[int] = None
    ):
        self.presenceDetected = presenceDetected
        self.presenceAmount = presenceAmount


class MovementMode(Enum):
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    IDLE = "IDLE"


# noinspection PyPep8Naming
class Blind:
    def __init__(
            self,
            blindLevel: Optional[int] = None,
            movementMode: Optional[MovementMode] = None,
            blindAngle: Optional[float] = None
    ):
        self.blindLevel = blindLevel
        self.movementMode = None if movementMode is None else movementMode.value
        self.blindAngle = blindAngle


# noinspection PyPep8Naming
class Gate:
    def __init__(
            self,
            openingState: Optional[OpeningState] = None,
            movementMode: Optional[MovementMode] = None,
    ):
        self.openingState = None if openingState is None else openingState.value
        self.movementMode = None if movementMode is None else movementMode.value


class Socket:
    def __init__(
            self,
            state: Optional[OnOffState] = None
    ):
        self.state = None if state is None else state.value


class Misc:
    def __init__(
            self,
            state: Optional[OnOffState] = None
    ):
        self.state = None if state is None else state.value


# noinspection PyPep8Naming
class Mailbox:
    def __init__(
            self,
            contentAvailable: Optional[bool] = None,
            contentCount: Optional[int] = None
    ):
        self.contentAvailable = contentAvailable
        self.contentCount = contentCount


# noinspection PyPep8Naming
class Doorbell:
    def __init__(
            self,
            ringTime: Optional[str] = None,
    ):
        self.ringTime = ringTime


class SmartHomeEventBuilder:
    # TODO apply some more validation...
    SHARED_TOPIC_ID = "smart-home"
    SMART_HOME_TOPIC_LAYOUT = name_for_shared_topic(
        SHARED_TOPIC_ID,
        "{}",  # house-identifier
        "{}",  # floor-identifier
        "{}",  # unit-identifier
        "{}",  # room-identifier
        "{}",  # category-identifier
        "{}"  # device-identifier
    )
    TOPIC_SEGMENT_PATTERN = re.compile("^[a-z0-9-.]+$")

    @staticmethod
    def indoor_climate(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            indoor_climate: IndoorClimate
    ) -> Event:
        payload = {
            'currentTemperature': indoor_climate.currentTemperature,
            'targetTemperature': indoor_climate.targetTemperature,
            'relativeHumidity': indoor_climate.relativeHumidity,
            'pressure': indoor_climate.pressure,
            'thermostatMode': indoor_climate.thermostatMode,
            'currentHeatingPower': indoor_climate.currentHeatingPower,
            'currentCoolingPower': indoor_climate.currentCoolingPower
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.INDOOR_CLIMATE, payload)

    @staticmethod
    def lighting(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            lighting: Lighting
    ) -> Event:
        payload = {
            'dimmingLevel': lighting.dimmingLevel,
            'color': lighting.color,
            'colorTemperature': lighting.colorTemperature,
            'state': lighting.state
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.LIGHTING, payload)

    @staticmethod
    def radiation(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            radiation: Radiation
    ) -> Event:
        payload = {
            'uvIndex': radiation.uvIndex,
            'brightness': radiation.brightness
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.RADIATION, payload)

    @staticmethod
    def window(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            window: Window
    ) -> Event:
        payload = {
            'openingState': window.openingState
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.WINDOW, payload)

    @staticmethod
    def unit_door(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            unit_door: UnitDoor
    ) -> Event:
        payload = {
            'openingState': unit_door.openingState
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.UNIT_DOOR, payload)

    @staticmethod
    def balcony_door(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            balcony_door: BalconyDoor
    ) -> Event:
        payload = {
            'openingState': balcony_door.openingState
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.BALCONY_DOOR, payload)

    @staticmethod
    def electricity(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            electricity: Electricity
    ) -> Event:
        payload = {
            'currentPower': electricity.currentPower,
            'current': electricity.current,
            'voltage': electricity.voltage
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.ELECTRICITY, payload)

    @staticmethod
    def presence(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            presence: Presence
    ) -> Event:
        payload = {
            'presenceDetected': presence.presenceDetected,
            'presenceAmount': presence.presenceAmount
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.PRESENCE, payload)

    @staticmethod
    def blind(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            blind: Blind
    ) -> Event:
        payload = {
            'blindLevel': blind.blindLevel,
            'movementMode': blind.movementMode,
            'blindAngle': blind.blindAngle
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.BLIND, payload)

    @staticmethod
    def gate(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            gate: Gate
    ) -> Event:
        payload = {
            'openingState': gate.openingState,
            'movementMode': gate.movementMode
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.GATE, payload)

    @staticmethod
    def socket(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            socket: Socket
    ) -> Event:
        payload = {
            'state': socket.state
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.SOCKET, payload)

    @staticmethod
    def misc(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            misc: Misc
    ) -> Event:
        payload = {
            'state': misc.state
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.MISC, payload)

    @staticmethod
    def mailbox(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            mailbox: Mailbox
    ) -> Event:
        payload = {
            'contentAvailable': mailbox.contentAvailable,
            'contentCount': mailbox.contentCount
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.MAILBOX, payload)

    @staticmethod
    def doorbell(
            house_identifier: str,
            floor_identifier: str,
            unit_identifier: str,
            room_identifier: str,
            device_identifier: str,
            doorbell: Doorbell
    ) -> Event:
        payload = {
            'ringTime': doorbell.ringTime
        }
        return SmartHomeEventBuilder._build_for_category(house_identifier, floor_identifier, unit_identifier,
                                                         room_identifier,
                                                         device_identifier, Category.DOORBELL, payload)

    @staticmethod
    def _build_for_category(house_identifier: str,
                            floor_identifier: str,
                            unit_identifier: str,
                            room_identifier: str,
                            device_identifier: str,
                            category: Category,
                            payload: dict) -> Event:
        if not SmartHomeEventBuilder.TOPIC_SEGMENT_PATTERN.match(house_identifier):
            raise ValueError("invalid house_identifier")
        if not SmartHomeEventBuilder.TOPIC_SEGMENT_PATTERN.match(floor_identifier):
            raise ValueError("invalid floor_identifier")
        if not SmartHomeEventBuilder.TOPIC_SEGMENT_PATTERN.match(unit_identifier):
            raise ValueError("invalid unit_identifier")
        if not SmartHomeEventBuilder.TOPIC_SEGMENT_PATTERN.match(room_identifier):
            raise ValueError("invalid room_identifier")
        if not SmartHomeEventBuilder.TOPIC_SEGMENT_PATTERN.match(device_identifier):
            raise ValueError("invalid device_identifier")
        if (
                (category is None) or
                (not isinstance(category, Category)) or
                (not SmartHomeEventBuilder.TOPIC_SEGMENT_PATTERN.match(category.value))
        ):
            raise ValueError("invalid category")

        if payload is None:
            raise ValueError("invalid payload")

        payload = SmartHomeEventBuilder._del_none(payload)  # get rid of None/nulls

        return Event(
            topic=SmartHomeEventBuilder.SMART_HOME_TOPIC_LAYOUT.format(
                house_identifier,
                floor_identifier,
                unit_identifier,
                room_identifier,
                category.value,
                device_identifier
            ),
            payload=payload
        )

    @staticmethod
    def _del_none(d):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.
        """
        if not isinstance(d, dict):
            return d
        return dict((k, SmartHomeEventBuilder._del_none(v)) for k, v in d.items() if v is not None)
