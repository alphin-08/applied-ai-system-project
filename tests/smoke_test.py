"""
Smoke test for the PawPal+ RAG pipeline.

Run with:  python smoke_test.py

Tests three scenarios:
  1. Dog with joint issues — checks health keyword retrieval
  2. Senior cat with medication — checks age bracket + task retrieval
  3. Pet with no health notes — checks graceful fallback
"""

from datetime import datetime, timedelta
from pawpal_system import CareTask, Owner, Pet, Scheduler
from retriever import retrieve_context
from ai_advisor import generate_care_advice


def today_at(hour: int, minute: int = 0) -> datetime:
    return datetime.today().replace(hour=hour, minute=minute, second=0, microsecond=0)


def divider(label: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print('='*60)


def run_scenario(label: str, pet: Pet, tasks: list[CareTask]) -> None:
    divider(label)

    # Build the owner + scheduler
    owner = Owner(name="Jordan", email="jordan@test.com")
    for task in tasks:
        pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    # ── Step 1: retriever ────────────────────────────────────────────────────
    task_types = [task.task_type for _, task in scheduler.plan]
    context = retrieve_context(pet, task_types)

    print("\n[RETRIEVED CONTEXT]")
    print(context)

    # ── Step 2: Claude API call ──────────────────────────────────────────────
    print("\n[CALLING GEMINI...]\n")
    advice = generate_care_advice(pet, scheduler.plan, scheduler.conflicts, context)

    print("[AI CARE SUMMARY]")
    print(advice)


# ── Scenario 1: young dog, joint issues, walk + medication conflict ──────────
pet1 = Pet(name="Mochi", species="dog", age=3, health_notes="joint stiffness")
tasks1 = [
    CareTask("Morning walk",  "walk",       30, "high",   today_at(7),  recurrence="daily"),
    CareTask("Medication",    "medication",  5, "high",   today_at(8)),
    CareTask("Breakfast",     "feeding",    15, "medium", today_at(8)),   # conflict with medication
]

# ── Scenario 2: senior cat, medication + appointment ────────────────────────
pet2 = Pet(name="Luna", species="cat", age=12, health_notes="kidney disease")
tasks2 = [
    CareTask("Morning meds",  "medication", 5,  "high",   today_at(8)),
    CareTask("Vet check-up",  "appointment", 60, "high",  today_at(10)),
]

# ── Scenario 3: healthy adult dog, no health notes ──────────────────────────
pet3 = Pet(name="Rex", species="dog", age=5, health_notes="")
tasks3 = [
    CareTask("Evening walk",  "walk",       45, "medium", today_at(18)),
    CareTask("Dinner",        "feeding",    10, "medium", today_at(19)),
]

if __name__ == "__main__":
    run_scenario("Scenario 1 — Young dog with joint issues", pet1, tasks1)
    run_scenario("Scenario 2 — Senior cat with kidney disease", pet2, tasks2)
    run_scenario("Scenario 3 — Healthy adult dog, no health notes", pet3, tasks3)

    print("\n" + "="*60)
    print("  Smoke test complete.")
    print("="*60 + "\n")
