# PawPal+ (Module 2 Project)

A smart pet care scheduling app built with Python and Streamlit. PawPal+ helps busy pet owners stay on top of daily care routines by organizing tasks using priority-based scheduling, conflict detection, and automatic recurring task management.

---

## Features

- **Register multiple pets** — add dogs, cats, or other animals with name, age, species, and health notes, all persisted across interactions via Streamlit session state.
- **Priority-first sorting** — the scheduler ranks tasks `high → medium → low`. A missed medication always appears before a routine walk, regardless of what time either is scheduled.
- **Chronological view** — toggle to a time-sorted view to see tasks in clock order — useful for planning your actual morning routine.
- **Conflict detection** — the scheduler checks every pair of tasks for overlapping time windows using interval intersection logic (`A.start < B.end AND B.start < A.end`). Conflicts surface as visible warnings in the UI — no crash, no silent data loss.
- **Recurring tasks** — mark a task as `daily` or `weekly`. When you complete it, the next occurrence is automatically created using Python's `timedelta`, keeping your routine going without manual re-entry.
- **Smart filtering** — filter the schedule by a specific pet or hide completed tasks to reduce noise in a busy day.
- **Mark done in the UI** — each task card has a "Mark done" button that calls the backend `complete_task()` method directly, triggering auto-scheduling for recurring tasks on the spot.

---

## Demo

<a href="/course_images/ai110/pawpaldemo.png" target="_blank">
  <img src='/course_images/ai110/pawpaldemo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

---

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/ -v
```

The suite contains **16 tests** across four categories:

| Category | What is tested |
|---|---|
| **Sorting** | Tasks added out of order are returned chronologically; high priority always ranks above low; time breaks ties within the same priority |
| **Recurrence** | Daily tasks auto-schedule for tomorrow; weekly tasks land 7 days out; non-recurring tasks produce no next occurrence |
| **Conflict detection** | Overlapping time windows are flagged; non-overlapping windows are clean; exact same start times are always caught |
| **Edge cases** | Pet with no tasks, owner with no pets, filtering by pet name, hiding completed tasks |

**Confidence level: 4 / 5 stars**

The core scheduling logic is well covered and all 16 tests pass. One star is held back because tasks are not persisted between sessions (session state resets on app restart), and the O(n²) conflict check has not been stress-tested with large task lists.

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

### Project structure

```
pawpal_system.py   # All backend logic — classes and scheduling algorithms
app.py             # Streamlit UI
main.py            # CLI demo script
tests/
  test_pawpal.py   # 16 automated tests
class_diagram.mmd  # Final UML diagram (Mermaid.js)
reflection.md      # Design and reflection notes
```
