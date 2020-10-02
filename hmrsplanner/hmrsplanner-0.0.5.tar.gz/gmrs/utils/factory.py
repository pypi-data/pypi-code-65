
from gmrs.model.capability import Capability
from gmrs.planner.sill_base import SkillBase
from gmrs.model.robot import Robot
from gmrs.model.property import Property


class property:
    def distance(value, unit):
        return Property('distrance', value, unit)

    def speed(value, unit):
        return Property('speed', value, unit)


def capability(label, **properties):
    cap = Capability(label)
    cap.addProperties(**properties)
    return cap


def skill(id):
    return SkillBase(id)


def robot(id):
    return Robot(id)
