# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a simple task list with four algorithmic features built into the `Scheduler` and `CareTask` classes:

- **Priority-first sorting** — tasks are ranked high → medium → low, with scheduled time as a tiebreaker. A missed medication always surfaces before a missed walk, regardless of clock time.
- **Chronological view** — `get_tasks_by_time()` re-sorts the plan by scheduled time so the owner can see what's coming up next on the clock, separate from the priority ranking.
- **Filtering** — `build_plan(pet_filter, show_completed)` lets the owner focus on a single pet or hide already-completed tasks, reducing noise in a busy day.
- **Recurring tasks** — tasks marked `daily` or `weekly` auto-schedule their next occurrence the moment they are completed via `Pet.complete_task()`, using Python's `timedelta` to calculate the exact next date.
- **Conflict detection** — after building the plan, `_detect_conflicts()` compares every pair of tasks using interval intersection (`A.start < B.end AND B.start < A.end`) and prints a warning for any overlapping time windows — no crash, just a clear alert.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
