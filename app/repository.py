from datetime import timedelta, date
from app.models import Habit, HabitLog
from app.exceptions import DuplicateLogError
from app.enums import HabitFrequency

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

    def get_current_streak(self, habit: Habit) -> int:
        logs = self.get_logs_for_habit(habit)
        current_date = date.today()
        streak = 0
        dates_set = {log.completed_date for log in logs}
        while current_date in dates_set:
            streak += 1
            current_date = current_date - timedelta(days=1)
        return streak

    def get_longest_streak(self, habit: Habit) -> int:
        logs = self.get_logs_for_habit(habit)
        longest = 1
        current = 1
        dates_set = sorted([log.completed_date for log in logs])
        if not dates_set:
            return 0
        for index in range(len(dates_set) - 1):
            if (dates_set[index + 1] - dates_set[index]).days == 1:
                current += 1
            else:
                longest = max(longest, current)
                current = 1
        longest = max(longest, current)
        return longest

    def get_completion_rate(self, habit: Habit, days: int = 30) -> float:
        logs = self.get_logs_for_habit(habit)
        dates_set = set(log.completed_date for log in logs)
        date_period = set(date.today() - timedelta(days=day_offset) for day_offset in range(days))
        completed_habits = len(dates_set & date_period)
        waited_days = days if habit.frequency == HabitFrequency.EVERYDAY else days / 7
        return (completed_habits / waited_days) * 100

