from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional

# Priority order used for sorting: higher index = higher urgency
PRIORITY_ORDER = {"low": 0, "medium": 1, "high": 2}

# How often a recurring task repeats
RECURRENCE_DAYS = {"daily": 1, "weekly": 7, "none": 0}


@dataclass
class CareTask:
    title: str
    task_type: str        # "walk" | "feeding" | "medication" | "appointment"
    duration_minutes: int
    priority: str         # "low" | "medium" | "high"
    scheduled_time: datetime
    completed: bool = False
    recurrence: str = "none"  # "none" | "daily" | "weekly"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today's date."""
        return self.scheduled_time.date() == date.today()

    def next_occurrence(self) -> Optional["CareTask"]:
        """Clone this task shifted forward by its recurrence interval, or return None if non-recurring."""
        if self.recurrence == "none":
            return None
        delta = timedelta(days=RECURRENCE_DAYS[self.recurrence])
        return CareTask(
            title=self.title,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            scheduled_time=self.scheduled_time + delta,
            recurrence=self.recurrence,
        )

    def end_time(self) -> datetime:
        """Return the datetime when this task ends by adding duration_minutes to scheduled_time."""
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)

    def conflicts_with(self, other: "CareTask") -> bool:
        """Return True if this task's time window overlaps with another task using interval intersection logic."""
        return self.scheduled_time < other.end_time() and other.scheduled_time < self.end_time()

    def __repr__(self) -> str:
        """Return a readable one-line summary of the task including priority, type, time, and status."""
        status = "done" if self.completed else "pending"
        time_str = self.scheduled_time.strftime("%H:%M")
        recur = f", {self.recurrence}" if self.recurrence != "none" else ""
        return (
            f"[{self.priority.upper()}] {self.title} "
            f"({self.task_type}{recur}, {self.duration_minutes}min @ {time_str}) — {status}"
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Attach a CareTask to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> List[CareTask]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def get_tasks_by_status(self, completed: bool) -> List[CareTask]:
        """Return only completed or only pending tasks for this pet."""
        return [t for t in self.tasks if t.completed == completed]

    def complete_task(self, task: CareTask) -> Optional[CareTask]:
        """Mark a task complete and, if it is recurring, append and return the next scheduled occurrence."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            self.tasks.append(next_task)
        return next_task

    def expand_recurring_tasks(self, days_ahead: int = 7) -> None:
        """Pre-populate the task list with future occurrences of all recurring tasks up to days_ahead days from today."""
        new_tasks: List[CareTask] = []
        cutoff = datetime.today() + timedelta(days=days_ahead)
        for task in self.tasks:
            next_task = task.next_occurrence()
            while next_task and next_task.scheduled_time <= cutoff:
                new_tasks.append(next_task)
                next_task = next_task.next_occurrence()
        self.tasks.extend(new_tasks)


class Owner:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_pet_by_name(self, name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None


class Scheduler:
    """
    Builds a prioritized daily care plan by gathering tasks from all of an
    owner's pets, filtering to today's date, and sorting by priority then time.

    Retrieval pattern:
        owner.get_pets()
          └── pet.get_tasks()
                └── filter: is_due_today() + optional pet/status filters
                      └── sort: priority (high->low), then scheduled_time
                            └── conflict check: overlapping windows flagged
    """

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler for an owner with an empty plan."""
        self.owner = owner
        self.plan: List[tuple[Pet, CareTask]] = []
        self.conflicts: List[tuple[CareTask, CareTask]] = []

    def build_plan(
        self,
        pet_filter: Optional[str] = None,
        show_completed: bool = True,
    ) -> None:
        """
        Gather tasks due today, with optional filtering by pet name or completion
        status, then sort high-priority first and detect time conflicts.
        """
        todays_tasks: List[tuple[Pet, CareTask]] = []

        for pet in self.owner.get_pets():
            # Filter 1: restrict to a specific pet if requested
            if pet_filter and pet.name.lower() != pet_filter.lower():
                continue

            for task in pet.get_tasks():
                if not task.is_due_today():
                    continue
                # Filter 2: optionally hide completed tasks
                if not show_completed and task.completed:
                    continue
                todays_tasks.append((pet, task))

        # Sort: descending priority, then ascending scheduled_time
        self.plan = sorted(
            todays_tasks,
            key=lambda pair: (
                -PRIORITY_ORDER[pair[1].priority],
                pair[1].scheduled_time,
            ),
        )

        # Detect conflicts after sorting (compare every pair of tasks)
        self._detect_conflicts()

    def _detect_conflicts(self) -> None:
        """Compare every pair of tasks in the plan and record overlapping time windows in self.conflicts."""
        self.conflicts = []
        tasks_only = [task for _, task in self.plan]
        for i in range(len(tasks_only)):
            for j in range(i + 1, len(tasks_only)):
                if tasks_only[i].conflicts_with(tasks_only[j]):
                    self.conflicts.append((tasks_only[i], tasks_only[j]))

    def get_next_task(self) -> Optional[tuple[Pet, CareTask]]:
        """Return the highest-priority incomplete task from today's plan."""
        for pet, task in self.plan:
            if not task.completed:
                return pet, task
        return None

    def get_tasks_by_time(self) -> List[tuple[Pet, CareTask]]:
        """Return today's plan re-sorted by scheduled_time ascending, ignoring priority order."""
        return sorted(self.plan, key=lambda pair: pair[1].scheduled_time)

    def explain_plan(self) -> str:
        """Return a human-readable summary of the day's plan with reasoning."""
        if not self.plan:
            return "No tasks scheduled for today."

        lines = [f"Daily care plan for {self.owner.name}:\n"]
        for i, (pet, task) in enumerate(self.plan, start=1):
            status = "[x]" if task.completed else "[ ]"
            time_str = task.scheduled_time.strftime("%H:%M")
            reason = (
                f"priority={task.priority}"
                if task.priority == "high"
                else f"priority={task.priority}, scheduled at {time_str}"
            )
            lines.append(
                f"  {i}. {status} [{pet.name}] {task.title} "
                f"@ {time_str} ({task.duration_minutes}min) — {reason}"
            )

        if self.conflicts:
            lines.append("\n  CONFLICTS DETECTED:")
            for a, b in self.conflicts:
                lines.append(
                    f"  !! '{a.title}' ({a.scheduled_time.strftime('%H:%M')}-"
                    f"{a.end_time().strftime('%H:%M')}) overlaps with "
                    f"'{b.title}' ({b.scheduled_time.strftime('%H:%M')}-"
                    f"{b.end_time().strftime('%H:%M')})"
                )

        incomplete = sum(1 for _, t in self.plan if not t.completed)
        lines.append(f"\n{incomplete} task(s) remaining.")
        return "\n".join(lines)
