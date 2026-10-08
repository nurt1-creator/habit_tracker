from datetime import date
from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency, HabitStatus
from app.user import User
from app.exceptions import DuplicateHabitError, DuplicateLogError, HabitArchivedError


if __name__ == "__main__":
    today_weekday = date.today().weekday()
    habit = Habit("Test", "desc", HabitFrequency.EVERYWEEK, weekday=today_weekday)
    repo = HabitLogRepository()
    repo.add(HabitLog(habit, date.today()))
    print(repo.get_completion_rate(habit, days=7))  # ожидаем 100.0