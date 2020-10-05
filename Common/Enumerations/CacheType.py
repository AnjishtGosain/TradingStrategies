from enum import Enum, auto

# Enumeration for caching


class CacheType(Enum):
    Csv = auto()
    Sql = auto()
    Bloomberg = auto()
