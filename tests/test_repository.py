import pytest
from datetime import date, timedelta
from app.models import HabitLog
from app.exceptions import DuplicateLogError


def test_repo_add(habit, repo, log):
    repo.add(log)
    assert len(repo.get_logs_for_habit(habit)) == 1

def test_repo_dublicate(habit, repo, log):
    repo.add(log)
    with pytest.raises(DuplicateLogError):
        repo.add(log)

def test_current_streak(habit, repo):
    assert repo.get_current_streak(habit) == 0

def test_current_streak_with_consecutive_days(habit, repo):
    repo.add(HabitLog(habit, date.today() - timedelta(days=2)))
    repo.add(HabitLog(habit, date.today() - timedelta(days=1)))
    repo.add(HabitLog(habit, date.today()))
    assert repo.get_current_streak(habit) == 3

def test_longest_streak_no_logs(habit, repo):
    assert repo.get_longest_streak(habit) == 0

def test_longest_streak_with_gap(habit, repo):
    repo.add(HabitLog(habit, date(2000, 1, 1)))
    repo.add(HabitLog(habit, date(2000, 1, 2)))
    repo.add(HabitLog(habit, date(2000, 1, 4)))
    repo.add(HabitLog(habit, date(2000, 1, 5)))
    repo.add(HabitLog(habit, date(2000, 1, 6)))
    assert repo.get_longest_streak(habit) == 3

def test_longest_streak_single_log(habit, repo, log):
    repo.add(log)
    assert repo.get_longest_streak(habit) == 1

def test_completion_rate(habit, repo):
    repo.add(HabitLog(habit, date.today() - timedelta(days=4)))
    repo.add(HabitLog(habit, date.today() - timedelta(days=3)))
    repo.add(HabitLog(habit, date.today() - timedelta(days=2)))
    repo.add(HabitLog(habit, date.today() - timedelta(days=1)))
    repo.add(HabitLog(habit, date.today()))
    assert repo.get_completion_rate(habit, days=5) == 100.0