from app.models import Habit, HabitLog
from app.exceptions import DuplicateLogError

class HabitLogRepository:
    def __init__(self) -> None:
        self._logs: list = []

    def add(self, log: HabitLog) -> None:
        for existing_log in self._logs:
            if existing_log.habit.name == log.habit.name and existing_log.completed_date == log.completed_date:
                raise DuplicateLogError("Duplicated habit")
        self._logs.append(log)

    def get_logs_for_habit(self, habit: Habit) -> list:
        return [wanted_log for wanted_log in self._logs if wanted_log.habit.name == habit.name]