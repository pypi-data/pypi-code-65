from typing import TypeVar, Generic, Tuple, Dict, Any, Type, Union


# = Basic customization begin ==========================================================================================


def m__init__(self, *args, **kwargs) -> None:
    self.__immutable_value = self.__base_type(*args, **kwargs)


def m__bytes__(self) -> bytes:
    return self.__immutable_value.__bytes__()


def m__int__(self) -> int:
    return self.__immutable_value.__int__()


def m__str__(self) -> str:
    return self.__immutable_value.__str__()


def m__bool__(self) -> bool:
    return self.__immutable_value.__bool__()


def m__format__(self, format_spec) -> str:
    return self.__immutable_value.__format__(format_spec)


def m__hash__(self) -> int:
    return self.__immutable_value.__hash__()


def m___lt__(self, other) -> bool:
    if type(self) == type(other):
        return self.__immutable_value < other.__immutable_value
    else:
        return self.__immutable_value < other


def m___le__(self, other) -> bool:
    if type(self) == type(other):
        return self.__immutable_value <= other.__immutable_value
    else:
        return self.__immutable_value <= other


def m___eq__(self, other) -> bool:
    if type(self) == type(other):
        return self.__immutable_value == other.__immutable_value
    else:
        return self.__immutable_value == other


def m___ne__(self, other) -> bool:
    if type(self) == type(other):
        return self.__immutable_value != other.__immutable_value
    else:
        return self.__immutable_value != other


def m___gt__(self, other) -> bool:
    if type(self) == type(other):
        return self.__immutable_value > other.__immutable_value
    else:
        return self.__immutable_value > other


def m___ge__(self, other) -> bool:
    if type(self) == type(other):
        return self.__immutable_value >= other.__immutable_value
    else:
        return self.__immutable_value >= other

# = Basic customization end ============================================================================================

# = Numeric emulation begin ============================================================================================


def m__add__(self, other: Any) -> Any:
    if type(self) == type(other):
        return self.__immutable_value + other.__immutable_value
    return self.__immutable_value + other


def m__sub__(self, other: Any) -> Any:
    if type(self) == type(other):
        return self.__immutable_value - other.__immutable_value
    return self.__immutable_value - other


def m__iadd__(self, other: Any) -> Any:
    if type(self) == type(other):
        self.__immutable_value += other.__immutable_value
    else:
        self.__immutable_value += other
    return self


def m__isub__(self, other: Any) -> Any:
    if type(self) == type(other):
        self.__immutable_value -= other.__immutable_value
    else:
        self.__immutable_value -= other
    return self

# = Numeric emulation end ==============================================================================================


T = TypeVar('T')


class MutableMeta(type, Generic[T]):
    __IMMUTABLE_TYPES = (
        bool,
        int,
        float,
        str,
        tuple,
    )

    __MAGIC_METHODS_MAPPING = {
        '__init__': m__init__,
        '__bytes__': m__bytes__,
        '__int__': m__int__,
        '__str__': m__str__,
        '__bool__': m__bool__,
        '__format__': m__format__,
        '__hash__': m__hash__,
        '__lt__': m___lt__,
        '__le__': m___le__,
        '__eq__': m___eq__,
        '__ne__': m___ne__,
        '__gt__': m___gt__,
        '__ge__': m___ge__,

        '__add__': m__add__,
        '__sub__': m__sub__,
    }

    __MAGIC_METHODS_IMETHODS_MAPPING = {
        '__add__': ('__iadd__', m__iadd__),
        '__sub__': ('__isub__', m__isub__),
    }

    @classmethod
    def __is_immutable(mcs, type_value: Type):
        return type_value in mcs.__IMMUTABLE_TYPES

    def __new__(mcs, name: str, bases: Tuple[T], namespace: Dict[str, Any]):
        if len(bases) != 1:
            raise ValueError(f'Expected single element as bases classes, but received {len(bases)}: {bases}')
        if not mcs.__is_immutable(bases[0]):
            return bases[0]
        result_cls = super(MutableMeta, mcs).__new__(mcs, name, tuple(), namespace)
        # Save immutable type information
        setattr(result_cls, '__base_type', bases[0])
        # Add types methods
        for mm_name, mm_value in mcs.__MAGIC_METHODS_MAPPING.items():
            if hasattr(bases[0], mm_name):
                setattr(result_cls, mm_name, mm_value)
                imm_name_value = mcs.__MAGIC_METHODS_IMETHODS_MAPPING.get(mm_name, None)
                if imm_name_value is not None:
                    setattr(result_cls, imm_name_value[0], imm_name_value[1])




        return result_cls


class MBoolean(bool, metaclass=MutableMeta):
    pass


class MInteger(int, metaclass=MutableMeta):
    pass


class MFloat(float, metaclass=MutableMeta):
    pass


class MString(str, metaclass=MutableMeta):
    pass


class MTuple(tuple, metaclass=MutableMeta):
    pass
