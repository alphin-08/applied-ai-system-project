from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import CareTask, Owner, Pet, Scheduler


# ── Shared helpers ─────────────────────────────────────────────────────────────

def today_at(hour, minute=0):
    """Return a datetime for today at the given hour and minute."""
    return datetime.today().replace(hour=hour, minute=minute, second=0, microsecond=0)


def make_task(title="Test walk", priority="medium", hour=9, minute=0,
              duration=20, task_type="walk", recurrence="none"):
    return CareTask(
        title=title,
        task_type=task_type,
        duration_minutes=duration,
        priority=priority,
        scheduled_time=today_at(hour, minute),
        recurrence=recurrence,
    )


def make_owner_with_pet():
    owner = Owner(name="Jordan", email="jordan@test.com")
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    return owner, pet


# ── Original tests (kept) ──────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """Marking a task complete flips its completed flag to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding tasks to a pet increases its task list length."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 2


# ── Sorting correctness ────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """get_tasks_by_time returns tasks earliest-first regardless of addition order."""
    owner, pet = make_owner_with_pet()
    # Added out of order: evening first, morning second
    pet.add_task(make_task("Evening walk", hour=18))
    pet.add_task(make_task("Morning walk", hour=7))
    pet.add_task(make_task("Noon feeding", hour=12))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()
    by_time = scheduler.get_tasks_by_time()

    times = [task.scheduled_time.hour for _, task in by_time]
    assert times == sorted(times), "Tasks are not in chronological order"


def test_build_plan_sorts_high_priority_before_low():
    """build_plan places high-priority tasks above low-priority tasks."""
    owner, pet = make_owner_with_pet()
    pet.add_task(make_task("Low task",  priority="low",  hour=7))
    pet.add_task(make_task("High task", priority="high", hour=18))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    priorities = [task.priority for _, task in scheduler.plan]
    assert priorities[0] == "high"
    assert priorities[-1] == "low"


def test_build_plan_time_breaks_priority_tie():
    """Within the same priority, earlier scheduled_time comes first."""
    owner, pet = make_owner_with_pet()
    pet.add_task(make_task("Late high",  priority="high", hour=14))
    pet.add_task(make_task("Early high", priority="high", hour=8))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    titles = [task.title for _, task in scheduler.plan]
    assert titles[0] == "Early high"
    assert titles[1] == "Late high"


# ── Recurrence logic ───────────────────────────────────────────────────────────

def test_daily_recurrence_creates_next_day_task():
    """Completing a daily task via complete_task auto-schedules tomorrow's instance."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = make_task("Morning walk", recurrence="daily")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert next_task is not None
    expected_date = (datetime.today() + timedelta(days=1)).date()
    assert next_task.scheduled_time.date() == expected_date


def test_weekly_recurrence_creates_next_week_task():
    """Completing a weekly task schedules the next occurrence 7 days later."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = make_task("Vet visit", recurrence="weekly")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert next_task is not None
    expected_date = (datetime.today() + timedelta(days=7)).date()
    assert next_task.scheduled_time.date() == expected_date


def test_non_recurring_task_creates_no_next_occurrence():
    """Completing a non-recurring task returns None and does not grow the task list."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = make_task("One-off appointment", recurrence="none")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert next_task is None
    assert len(pet.get_tasks()) == 1  # no new task appended


def test_recurring_task_appended_to_pet():
    """After completing a daily task, the pet's task list grows by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = make_task("Morning walk", recurrence="daily")
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1

    pet.complete_task(task)
    assert len(pet.get_tasks()) == 2


# ── Conflict detection ─────────────────────────────────────────────────────────

def test_overlapping_tasks_detected_as_conflict():
    """Two tasks whose time windows overlap are flagged in scheduler.conflicts."""
    owner, pet = make_owner_with_pet()
    # Task A: 07:00 for 30 min → ends 07:30
    # Task B: 07:15 for 20 min → starts inside Task A's window
    pet.add_task(make_task("Task A", hour=7, minute=0,  duration=30))
    pet.add_task(make_task("Task B", hour=7, minute=15, duration=20))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    assert len(scheduler.conflicts) == 1


def test_non_overlapping_tasks_have_no_conflicts():
    """Tasks with no time window overlap produce an empty conflicts list."""
    owner, pet = make_owner_with_pet()
    # Task A ends at 07:30, Task B starts at 08:00 — no overlap
    pet.add_task(make_task("Task A", hour=7, minute=0,  duration=30))
    pet.add_task(make_task("Task B", hour=8, minute=0,  duration=20))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    assert len(scheduler.conflicts) == 0


def test_exact_same_start_time_is_a_conflict():
    """Two tasks starting at the identical time are always a conflict."""
    owner, pet = make_owner_with_pet()
    pet.add_task(make_task("Task A", hour=9, minute=0, duration=15))
    pet.add_task(make_task("Task B", hour=9, minute=0, duration=10))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    assert len(scheduler.conflicts) >= 1


# ── Edge cases ─────────────────────────────────────────────────────────────────

def test_pet_with_no_tasks_produces_empty_plan():
    """A pet with zero tasks results in an empty schedule, not an error."""
    owner, _ = make_owner_with_pet()  # pet has no tasks added
    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    assert scheduler.plan == []
    assert scheduler.conflicts == []


def test_owner_with_no_pets_produces_empty_plan():
    """An owner with no registered pets produces an empty plan."""
    owner = Owner(name="Empty", email="empty@test.com")
    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    assert scheduler.plan == []


def test_filter_by_pet_name_excludes_other_pets():
    """build_plan(pet_filter=name) returns only that pet's tasks."""
    owner = Owner(name="Jordan", email="j@test.com")
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(make_task("Mochi walk"))
    luna.add_task(make_task("Luna meds"))

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan(pet_filter="Luna")

    pet_names = {pet.name for pet, _ in scheduler.plan}
    assert pet_names == {"Luna"}


def test_show_completed_false_hides_done_tasks():
    """build_plan(show_completed=False) excludes completed tasks from the plan."""
    owner, pet = make_owner_with_pet()
    done_task    = make_task("Done task",    hour=8)
    pending_task = make_task("Pending task", hour=9)

    done_task.mark_complete()
    pet.add_task(done_task)
    pet.add_task(pending_task)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan(show_completed=False)

    titles = [task.title for _, task in scheduler.plan]
    assert "Done task" not in titles
    assert "Pending task" in titles
