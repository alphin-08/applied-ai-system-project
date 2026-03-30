from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

# Priority order used for sorting: higher index = higher urgency
PRIORITY_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass
class CareTask:
    title: str
    task_type: str        # "walk" | "feeding" | "medication" | "appointment"
    duration_minutes: int
    priority: str         # "low" | "medium" | "high"
    scheduled_time: datetime
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today's date."""
        return self.scheduled_time.date() == date.today()

    def __repr__(self) -> str:
        """Return a readable one-line summary of the task including priority, type, time, and status."""
        status = "done" if self.completed else "pending"
        time_str = self.scheduled_time.strftime("%H:%M")
        return (
            f"[{self.priority.upper()}] {self.title} "
            f"({self.task_type}, {self.duration_minutes}min @ {time_str}) — {status}"
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


class Scheduler:
    """
    Builds a prioritized daily care plan by gathering tasks from all of an
    owner's pets, filtering to today's date, and sorting by priority then time.

    Retrieval pattern:
        owner.get_pets()
          └── pet.get_tasks()
                └── filter: task.is_due_today()
                      └── sort: priority (high→low), then scheduled_time
    """

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler for an owner with an empty plan."""
        self.owner = owner
        self.plan: List[tuple[Pet, CareTask]] = []  # (pet, task) pairs

    def build_plan(self) -> None:
        """Gather all tasks due today from every pet, sorted high-priority first then by time."""
        todays_tasks: List[tuple[Pet, CareTask]] = []

        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.is_due_today():
                    todays_tasks.append((pet, task))

        # Sort: descending priority, then ascending scheduled_time
        self.plan = sorted(
            todays_tasks,
            key=lambda pair: (
                -PRIORITY_ORDER[pair[1].priority],
                pair[1].scheduled_time,
            ),
        )

    def get_next_task(self) -> Optional[tuple[Pet, CareTask]]:
        """Return the highest-priority incomplete task from today's plan."""
        for pet, task in self.plan:
            if not task.completed:
                return pet, task
        return None

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

        incomplete = sum(1 for _, t in self.plan if not t.completed)
        lines.append(f"\n{incomplete} task(s) remaining.")
        return "\n".join(lines)
