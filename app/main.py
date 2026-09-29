from enum import Enum
from datetime import date

class HabitStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class HabitFrequency(Enum):
    EVERYDAY = "everyday"
    EVERYWEEK = "everyweek"


class HabitArchivedError(Exception):
    pass


class Habit:
    def __init__(self, name: str, description: str, frequency: HabitFrequency) -> None:
        self.check_empty_name(name)
    
        self.name = name.strip()
        self.description = description.strip()
        self.frequency = frequency
        self._status: HabitStatus = HabitStatus.ACTIVE

        self._created_at = date.today()

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, val: str) -> None:
        self.check_empty_name(val)
        self._name = val.strip()

    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, val: str) -> None:
        self._description = val.strip()

    def check_correct_freq_enum(self, val: HabitFrequency) -> None:
        if not isinstance(val, HabitFrequency):
            raise TypeError("Incorrect Enum")

    @property
    def frequency(self) -> HabitFrequency:
        return self._frequency
    
    @frequency.setter
    def frequency(self, val: HabitFrequency) -> None:
        self.check_correct_freq_enum(val)
        self._frequency = val

    def check_empty_name(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Habit is empty")

    def archive(self) -> None:
        self._status = HabitStatus.ARCHIVED

    def activate(self) -> None:
        self._status = HabitStatus.ACTIVE

    @property
    def status(self) -> HabitStatus:
        return self._status

    @property
    def created_at(self) -> date:
        return self._created_at


class HabitLog:
    def __init__(self, habit: Habit, completed_date: date):
        if completed_date > date.today():
            raise ValueError("Completed date can not be in future")

        if habit.status == HabitStatus.ARCHIVED:
            raise HabitArchivedError("Habit archived")

        self.completed_date = completed_date
        self.habit = habit

if __name__ == "__main__":
    habit = Habit("Brainstorm", "Study 2 hours everyday", HabitFrequency.EVERYDAY)

# ===== TESTS =====

    habit.archive()
    print(HabitLog(habit, date.today()))
