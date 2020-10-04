from gmrs.model.capability import Capability


class MoveCapability(Capability):
    privide = 'move'
    configs = {
        'speed': None
    }
