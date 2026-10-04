import pytest
from app.exceptions import DuplicateHabitError


def test_user_add_habit(user, habit):
    user.add_habit(habit)
    assert user.get_habit_by_name(habit.name) is habit

def test_user_dublicate_habit(user, habit):
    user.add_habit(habit)
    with pytest.raises(DuplicateHabitError):
        user.add_habit(habit)
