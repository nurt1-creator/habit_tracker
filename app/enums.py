from enum import Enum

class HabitStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class HabitFrequency(Enum):
    EVERYDAY = "everyday"
    EVERYWEEK = "everyweek"