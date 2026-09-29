from datetime import date
from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency


if __name__ == "__main__":
    habit1 = Habit("Brainstorm", "Study 2 hours everyday", HabitFrequency.EVERYDAY)

    repo = HabitLogRepository()
    repo.add(HabitLog(habit1, date(2026, 9, 27)))
    repo.add(HabitLog(habit1, date(2026, 9, 28)))
    repo.add(HabitLog(habit1, date.today()))

    print(repo.get_logs_for_habit(habit1))