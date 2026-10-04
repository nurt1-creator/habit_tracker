import pytest
from app.models import Habit
from app.enums import HabitFrequency
from app.enums import HabitStatus


@pytest.mark.parametrize("invalid_name", ["", "   "])
def test_empty_name_raises_error(invalid_name):
    with pytest.raises(ValueError):
        Habit(invalid_name, "описание", HabitFrequency.EVERYDAY)

def test_habit_created_with_valid_data(habit):
    assert habit.name == "Reading"
    assert habit.description == "Read 10 pages"
    assert habit.frequency == HabitFrequency.EVERYDAY
    assert habit.status == HabitStatus.ACTIVE

def test_habit_archived_correct(habit):
    habit.archive()
    assert habit.status == HabitStatus.ARCHIVED