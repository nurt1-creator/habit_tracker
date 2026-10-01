from datetime import date, timedelta
from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency
from app.user import User

if __name__ == "__main__":
    habit1 = Habit("Brainstorm", "Study 2 hours everyday", HabitFrequency.EVERYDAY)
    habit2 = Habit("BrainstormUltra", "Study 2 hours everyday", HabitFrequency.EVERYWEEK)
    repo = HabitLogRepository()

    repo.add(HabitLog(habit1, date.today() - timedelta(days=4)))
    repo.add(HabitLog(habit1, date.today() - timedelta(days=3)))
    repo.add(HabitLog(habit1, date.today() - timedelta(days=2)))
    repo.add(HabitLog(habit1, date.today() - timedelta(days=1)))
    repo.add(HabitLog(habit1, date.today()))

    repo.add(HabitLog(habit2, date.today()))

    print(repo.get_completion_rate(habit1, days=30))
    print(repo.get_completion_rate(habit2, days=30))