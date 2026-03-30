from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class CareTask:
    title: str
    task_type: str  # "walk" | "feeding" | "medication" | "appointment"
    duration_minutes: int
    priority: str   # "low" | "medium" | "high"
    scheduled_time: datetime
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_due_today(self) -> bool:
        pass

    def __repr__(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        pass

    def get_tasks(self) -> List[CareTask]:
        pass


class Owner:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> List[Pet]:
        pass


class Scheduler:
    def __init__(self, pet: Pet, date: date) -> None:
        self.pet = pet
        self.date = date
        self.plan: List[CareTask] = []

    def build_plan(self) -> None:
        pass

    def get_next_task(self) -> Optional[CareTask]:
        pass

    def explain_plan(self) -> str:
        pass
