import pytest

from validation import make_task, validate_task_inputs


def test_bad_time_rejected():
    with pytest.raises(ValueError):
        make_task("Walk", "25:00")


def test_empty_description_rejected():
    with pytest.raises(ValueError):
        make_task("   ", "09:00")


def test_bad_frequency_rejected():
    with pytest.raises(ValueError):
        make_task("Walk", "09:00", "hourly")


def test_valid_input_builds_task():
    task = make_task("  Walk  ", "09:05", "daily")
    assert task.description == "Walk" and task.time == "09:05"


def test_all_problems_reported_together():
    assert len(validate_task_inputs("", "99:99", "never")) == 3