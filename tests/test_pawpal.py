from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import CareTask, Pet


def make_task(priority="medium"):
    return CareTask(
        title="Test walk",
        task_type="walk",
        duration_minutes=20,
        priority=priority,
        scheduled_time=datetime.today().replace(hour=9, minute=0, second=0, microsecond=0),
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 2
