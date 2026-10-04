import pytest
from datetime import date
from app.models import Habit, HabitLog
from app.enums import HabitFrequency
from app.repository import HabitLogRepository
from app.user import User


@pytest.fixture
def habit():
    return Habit("Reading", "Read 10 pages", HabitFrequency.EVERYDAY)

@pytest.fixture
def repo():
    return HabitLogRepository()

@pytest.fixture
def log(habit):
    return HabitLog(habit, date.today())

@pytest.fixture
def user():
    return User("John")