from enum import Enum

class HabitStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class Habit:
    def __init__(self, name: str, description: str) -> None:
        self.check_empty_name(name)
    
        self.name = name.strip()
        self.description = description.strip()
        self._status: HabitStatus = HabitStatus.ACTIVE

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

    def __repr__(self) -> str:
        return f"Habit(name={self.name!r}, description={self.description!r}, status={self.status!r})"

    
habit = Habit("jambo", "Читать 10 страниц в день")
print(habit.status)
habit.archive()
habit.status = HabitStatus.ARCHIVED
print(habit.status)