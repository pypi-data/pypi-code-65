from snowday.types.base import DataType


VARCHAR = DataType(name="varchar")

CHAR = DataType(name="char")

CHARACTER = DataType(name="character")

STRING = DataType(name="string")  # Synonymous with VARCHAR

TEXT = DataType(name="text")  # Synonymous with VARCHAR

BINARY = DataType(
    name="binary"
)  # No notion of unicode characters, so length always measured in terms of bytes

VARBINARY = DataType(name="varbinary")  # Synonymous with BINARY
