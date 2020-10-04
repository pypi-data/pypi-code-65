import re

import arrow
from ics import Calendar, Event

from .util import TEACHERS


class CalendarWrapper:

    DATE_FMT = "YYYY-MM-DDTHH:mm:ss+11:00"
    EDUMATE_FMT = "YYYY-MM-DD HH:mm:SS"

    EDUMTE_RE = r"^\S+ (.*) (\d+|\w+|\d+\w+) \((\w\d{3}|.*).*\).*"

    def __init__(self) -> None:
        self.calendar = Calendar()

    def add_classes(self, timetable) -> None:
        for day in timetable:
            for cls in day["events"]:
                match = re.match(self.EDUMTE_RE, cls["activityName"])
                subject = match.group(1) if match else None
                room = match.group(3) if match else None
                begin = arrow.get(cls["startDateTime"]["date"], self.EDUMATE_FMT)
                if "href" in cls["links"][0].keys():
                    *_, email = cls["links"][0]["href"].split("=")
                    abreviated, *_ = email.split("@")
                    teacher = TEACHERS.get(abreviated, abreviated)
                else:
                    teacher = None

                # Make sure extension classes start at 7:30
                if "Extension" in subject:
                    begin = begin.replace(hour=7, minute=30)

                hour, minute = map(int, cls["time"].split(":"))
                end = begin.replace(hour=hour, minute=minute)

                event = Event(
                    name=subject,
                    location=room,
                    description=teacher,
                    begin=begin.format(self.DATE_FMT),
                    end=end.format(self.DATE_FMT),
                )

                self.calendar.events.add(event)

    def __iter__(self) -> None:
        return self.calendar.__iter__()
