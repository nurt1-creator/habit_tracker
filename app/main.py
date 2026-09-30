from datetime import date, timedelta
from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency
from app.user import User

if __name__ == "__main__":
    habit1 = Habit("Brainstorm", "Study 2 hours everyday", HabitFrequency.EVERYDAY)
    repo = HabitLogRepository()

    # repo.add(HabitLog(habit1, date.today() - timedelta(days=7)))
    # repo.add(HabitLog(habit1, date.today() - timedelta(days=6)))
    # repo.add(HabitLog(habit1, date.today() - timedelta(days=5)))
    # repo.add(HabitLog(habit1, date.today() - timedelta(days=4)))
    # repo.add(HabitLog(habit1, date.today() - timedelta(days=1)))
    repo.add(HabitLog(habit1, date.today()))

    # print(f"current: {repo.get_current_streak(habit1)}")
    print(f"longest: {repo.get_longest_streak(habit1)}")