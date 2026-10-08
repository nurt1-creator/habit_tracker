from datetime import date, timedelta

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from app.models import Habit, HabitLog
from app.repository import HabitLogRepository
from app.enums import HabitFrequency, HabitStatus
from app.user import User
from app.exceptions import DuplicateHabitError, DuplicateLogError, HabitArchivedError

console = Console()

MENU_TEXT = (
    "[bold]1.[/bold] Add habit\n"
    "[bold]2.[/bold] Mark habit\n"
    "[bold]3.[/bold] Show statistics\n"
    "[bold]4.[/bold] Change habit status\n"
    "[bold]5.[/bold] Exit"
)


def show_menu() -> None:
    console.print(Panel(MENU_TEXT, title="[bold cyan]Habit Tracker[/bold cyan]", border_style="cyan"))


def success(message: str) -> None:
    console.print(f"[bold green]✓[/bold green] {message}")


def error(message: str) -> None:
    console.print(f"[bold red]✗ Error:[/bold red] {message}")


def warning(message: str) -> None:
    console.print(f"[bold yellow]![/bold yellow] {message}")


def find_habit(user: User) -> Habit | None:
    habit_name = Prompt.ask("Habit name")
    habit = user.get_habit_by_name(habit_name)
    if habit is None:
        warning("Habit not found!")
        return None
    return habit


if __name__ == "__main__":
    console.print(Panel.fit("[bold magenta]Welcome to Habit Tracker[/bold magenta]"))
    username = Prompt.ask("What is your name?")
    user = User(username)
    repo = HabitLogRepository()

    while True:
        show_menu()
        try:
            choice = int(Prompt.ask("Choose an option"))
            match choice:
                case 1:
                    habit_name = Prompt.ask("Habit name")
                    habit_description = Prompt.ask("Habit description (can be empty)", default="")
                    try:
                        habit_frequency = int(
                            Prompt.ask("1. Everyday\n2. Everyweek\nHabit frequency")
                        )
                        match habit_frequency:
                            case 1:
                                habit_frequency = HabitFrequency.EVERYDAY
                                habit_weekday = None
                            case 2:
                                habit_frequency = HabitFrequency.EVERYWEEK
                                habit_weekday = int(
                                    Prompt.ask("1. Monday\n2. Tuesday\n3. Wednesday\n4. Thursday\n5. Friday\n6. Saturday\n7. Sunday\nWeek day")
                                ) - 1
                            case _:
                                warning("Unknown action")
                                continue
                    except ValueError:
                        error("Only numbers allowed!")
                        continue

                    try:
                        created_habit = Habit(habit_name, habit_description, habit_frequency, habit_weekday)
                        user.add_habit(created_habit)
                        success(f"Habit '{created_habit.name}' added!")
                    except (ValueError, DuplicateHabitError, IndexError) as e:
                        error(str(e))

                case 2:
                    wanted_habit = find_habit(user)
                    if wanted_habit is None:
                        continue
                    try:
                        log = HabitLog(wanted_habit, date.today())
                        repo.add(log)
                        success(f"'{wanted_habit.name}' marked as completed!")
                    except (DuplicateLogError, HabitArchivedError) as e:
                        error(str(e))

                case 3:
                    wanted_habit = find_habit(user)
                    if wanted_habit is None:
                        continue

                    table = Table(title=f"Statistics for '{wanted_habit.name}'", border_style="cyan")
                    table.add_column("Metric", style="bold")
                    table.add_column("Value", justify="right")
                    table.add_row("Status", wanted_habit.status.value)
                    if wanted_habit.frequency == HabitFrequency.EVERYWEEK:
                        WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        table.add_row("Week Day", f"{WEEKDAYS[wanted_habit.weekday]}")
                    table.add_row("Current streak", f"{repo.get_current_streak(wanted_habit)} days")
                    table.add_row("Longest streak", f"{repo.get_longest_streak(wanted_habit)} days")
                    table.add_row(
                        "Completion rate (30 days)",
                        f"{round(repo.get_completion_rate(wanted_habit, days=30), 2)}%",
                    )
                    console.print(table)

                case 4:
                    wanted_habit = find_habit(user)
                    if wanted_habit is None:
                        continue

                    if wanted_habit.status == HabitStatus.ARCHIVED:
                        warning("Habit status is 'Archived'")
                        confirm = Prompt.ask("Activate this habit?", choices=["yes", "no"], default="no")
                        if confirm == "yes":
                            wanted_habit.activate()
                            success("Habit activated!")
                        else:
                            warning("Abandoned!")
                    else:
                        warning("Habit status is 'Active'")
                        confirm = Prompt.ask("Archive this habit?", choices=["yes", "no"], default="no")
                        if confirm == "yes":
                            wanted_habit.archive()
                            success("Habit archived!")
                        else:
                            warning("Abandoned!")

                case 5:
                    console.print("[bold magenta]Goodbye![/bold magenta]")
                    break

                case _:
                    warning("Unknown action")

        except ValueError:
            error("Only numbers allowed!")