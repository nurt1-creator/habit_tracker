from datetime import date
from app.enums import HabitStatus, HabitFrequency
from app.exceptions import HabitArchivedError

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

    def check_empty_name(self, name: str) -> None:
            if not name.strip():
                raise ValueError("Habit is empty")

    @property
    def frequency(self) -> HabitFrequency:
        return self._frequency
    
    @frequency.setter
    def frequency(self, val: HabitFrequency) -> None:
        self.check_correct_freq_enum(val)
        self._frequency = val

    def check_correct_freq_enum(self, val: HabitFrequency) -> None:
            if not isinstance(val, HabitFrequency):
                raise TypeError("Incorrect Enum")
    
    @property
    def status(self) -> HabitStatus:
        return self._status
    
    def archive(self) -> None:
            self._status = HabitStatus.ARCHIVED

    def activate(self) -> None:
        self._status = HabitStatus.ACTIVE
    
    @property
    def created_at(self) -> date:
        return self._created_at

    def __repr__(self) -> str:
        return f"Habit(name={self.name!r}, description={self.description!r}, status={self.status!r}, frequency={self.frequency!r})"


class HabitLog:
    def __init__(self, habit: Habit, completed_date: date):
        if completed_date > date.today():
            raise ValueError("Completed date can not be in future")

        if habit.status == HabitStatus.ARCHIVED:
            raise HabitArchivedError("Habit archived")

        self.completed_date = completed_date
        self.habit = habit

    def __repr__(self):
        return f"HabitLog(name={self.habit.name!r}, completed_date={self.completed_date!r})"