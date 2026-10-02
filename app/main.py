from datetime import date, timedelta
from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency, HabitStatus
from app.user import User
from app.exceptions import DuplicateHabitError, DuplicateLogError, HabitArchivedError

if __name__ == "__main__":
    user = User(input("What is your name?: "))
    repo = HabitLogRepository()
    while True:
        print("1. Add habit\n"
                    "2. Mark habit\n"
                    "3. Show statistics\n"
                    "4. Change habit status\n"
                    "5. Exit")
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
                    habit_name = input("Habit name: ")
                    wanted_habit = user.get_habit_by_name(habit_name)
                    if wanted_habit is None:
                        print("Habit not found!")
                        continue
                    try:
                        log = HabitLog(wanted_habit, date.today())
                        repo.add(log)
                        print("Habit marked as completed!")
                    except (DuplicateLogError, HabitArchivedError) as e:
                        print(f"Error: {e}")
                case 3:
                    habit_name = input("Habit name: ")
                    wanted_habit = user.get_habit_by_name(habit_name)
                    if wanted_habit is None:
                        print("Habit not found!")
                        continue
                    print(f"======STATISTICS======\n"
                    f"Current streak: {repo.get_current_streak(wanted_habit)}\n"
                    f"Longest streak: {repo.get_longest_streak(wanted_habit)}\n"
                    f"Completion rate: {round(repo.get_completion_rate(wanted_habit, days=30), 2)}%"
                    )
                case 4:
                    habit_name = input("Habit name: ")
                    wanted_habit = user.get_habit_by_name(habit_name)
                    if wanted_habit is None:
                        print("Habit not found!")
                        continue
                    if wanted_habit.status == HabitStatus.ARCHIVED:
                        print("Habit status is 'Archived'")
                        confirm = input("Do you wanna activate habit?(type Yes to confirm): ")
                        if confirm.lower() == "yes":
                            wanted_habit.activate()
                            print("Habit activated!")
                            continue
                        else:
                            print("Abandoned!")
                            continue
                    if wanted_habit.status == HabitStatus.ACTIVE:
                        print("Habit status is 'Active'")
                        confirm = input("Do you wanna archive habit?(type Yes to confirm): ")
                        if confirm.lower() == "yes":
                            wanted_habit.archive()
                            print("Habit archived!")
                            continue
                        else:
                            print("Abandoned!")
                            continue
                case 5:
                    break
                case _:
                    print("Unknown action")
        except ValueError:
            print("Only numbers allowed!")