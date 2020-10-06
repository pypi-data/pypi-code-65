import enum


class DetailedState(enum.IntEnum):
    DISABLEDSTATE = 1
    ENABLEDSTATE = 2
    FAULTSTATE = 3
    OFFLINESTATE = 4
    STANDBYSTATE = 5
    MOVINGSTATE = 6
