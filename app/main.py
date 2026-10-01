from datetime import date, timedelta
from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency
from app.user import User
from app.exceptions import DuplicateHabitError

if __name__ == "__main__":
    user = User(input("What is your name?: "))
    repo = HabitLogRepository()
    while True:
        print("1. Add habit\n" \
                    "2. Exit")
        try:
            choice = int(input())
            match choice:
                case 1:
                    habit_name = input("Habit name: ")
                    habit_description = input("Habit description(can be empty): ")
                    try:
                        habit_frequency = int(input("1.Everyday\n2.Everyweek\nHabit frequency: "))
                        match habit_frequency:
                            case 1:
                                habit_frequency = HabitFrequency.EVERYDAY
                            case 2:
                                habit_frequency = HabitFrequency.EVERYWEEK
                            case _:
                                print("Unknown action")
                                continue
                    except ValueError:
                        print("Only numbers allowed!")
                        continue
                    try:
                        created_habit = Habit(habit_name, habit_description, habit_frequency)
                        user.add_habit(created_habit)
                        print("Habit added!")
                    except (ValueError, DuplicateHabitError) as e:
                        print(f"Error: {e}")
                case 2:
                    break
                case _:
                    print("Unknown action")
        except ValueError:
            print("Only numbers allowed!")