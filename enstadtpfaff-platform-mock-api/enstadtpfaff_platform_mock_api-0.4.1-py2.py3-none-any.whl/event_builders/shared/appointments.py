from enum import Enum
from typing import List, Optional

from enstadtpfaff_platform_mock_api.event import Event
from enstadtpfaff_platform_mock_api.util.topic_util import name_for_shared_topic


class AppointmentType(Enum):
    PERSONAL = 'PERSONAL'
    BUSINESS = 'BUSINESS'
    FREETIME = 'FREETIME'
    MISC = 'MISC'


# noinspection PyPep8Naming
class Appointment:
    def __init__(
            self,
            appointmentId: str,
            calendarId: str,
            calendarOwnerId: str,
            title: str,
            start: str,
            end: str,
            appointmentType: AppointmentType,
            description: Optional[str] = None,
            attendees: Optional[List[str]] = None,
            isAllDay: Optional[bool] = None,
            isPrivate: Optional[bool] = None,
            location: Optional[str] = None,
            tags: Optional[List[str]] = None
    ):
        self.appointmentId = appointmentId
        self.calendarId = calendarId
        self.calendarOwnerId = calendarOwnerId
        self.title = title
        self.start = start
        self.end = end
        self.appointmentType = None if appointmentType is None else appointmentType.value
        self.description = description
        self.attendees = attendees
        self.isAllDay = isAllDay
        self.isPrivate = isPrivate
        self.location = location
        self.tags = tags


class AppointmentsEventBuilder:
    SHARED_TOPIC_ID = "appointments"
    APPOINTMENT_CREATED_TOPIC = name_for_shared_topic(
        SHARED_TOPIC_ID,
        "appointment-created"
    )
    APPOINTMENT_UPDATED_TOPIC = name_for_shared_topic(
        SHARED_TOPIC_ID,
        "appointment-updated"
    )
    APPOINTMENT_DELETED_TOPIC = name_for_shared_topic(
        SHARED_TOPIC_ID,
        "appointment-deleted"
    )

    @staticmethod
    def appointment_created(
            appointment: Appointment
    ) -> Event:
        payload = AppointmentsEventBuilder._del_none(vars(appointment))
        return Event(
            AppointmentsEventBuilder.APPOINTMENT_CREATED_TOPIC,
            payload
        )

    @staticmethod
    def appointment_updated(
            appointment: Appointment
    ) -> Event:
        payload = AppointmentsEventBuilder._del_none(vars(appointment))
        return Event(
            AppointmentsEventBuilder.APPOINTMENT_UPDATED_TOPIC,
            payload
        )

    @staticmethod
    def appointment_deleted(
            appointment: Appointment
    ) -> Event:
        payload = AppointmentsEventBuilder._del_none(vars(appointment))
        return Event(
            AppointmentsEventBuilder.APPOINTMENT_DELETED_TOPIC,
            payload
        )

    @staticmethod
    def _del_none(d):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.
        """
        if not isinstance(d, dict):
            return d
        return dict((k, AppointmentsEventBuilder._del_none(v)) for k, v in d.items() if v is not None)
