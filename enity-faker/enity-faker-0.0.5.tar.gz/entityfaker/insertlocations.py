from enum import IntEnum
class InsertLocation(IntEnum):
    KeyValue = 1,
    SameLineBeforeEntity = 2,
    SameLineAfterEntity = 3,
    DiffLineBeforeEntity = 4,
    DiffLineAfterEntity = 5,
    InFileName = 6