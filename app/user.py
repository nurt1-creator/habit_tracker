from app.models import Habit
from app.exceptions import DuplicateHabitError

class User:
    def __init__(self, name: str) -> None:
        self.check_empty_name(name)
        self.name = name
        self._habits = []

    def check_empty_name(self, name: str) -> None:
            if not name.strip():
                raise ValueError("Habit is empty")

    def add_habit(self, habit: Habit) -> None:
        for existing_habit in self._habits:
            if existing_habit.name == habit.name:
                raise DuplicateHabitError("Duplicated habit")
        self._habits.append(habit)

    def get_habit_by_name(self, name: str):
        for habit in self._habits:
            if habit.name == name:
                return habit
        return None

    def __repr__(self) -> str:
        return f"User(name={self.name!r}, habits={self._habits})"
        