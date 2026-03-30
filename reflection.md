# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform in PawPal+:

1. **Add a pet** — The user registers a pet by providing its name, species, age, and any special health notes. This creates a profile that all future tasks and schedules are tied to, making it the foundation of the entire system.

2. **Schedule a care task** — The user creates a task for a specific pet (such as a walk, feeding, medication dose, or vet appointment), setting a date, time, and priority level. This is the primary daily interaction — building out the pet's care calendar.

3. **View today's tasks** — The user sees a prioritized list of all care tasks due today across all their pets. The system sorts tasks by urgency and type so the owner always knows what needs attention first.

The design uses four classes, each with a single clear responsibility:

**Owner** is the top-level user of the system. It holds the owner's name and email, and maintains a list of their pets. Its responsibility is to act as the entry point — all pets and their care flows through the owner. It was implemented as a regular class because it manages state and behavior beyond simple data storage.

**Pet** represents a registered animal in the system. It stores the pet's name, species, age, and any health notes, and holds the full list of CareTask objects assigned to it. Its responsibility is to be the central data record for one pet — a container that tasks are attached to and retrieved from. It was implemented as a Python dataclass to keep the definition clean and auto-generate the constructor.

**CareTask** represents one unit of care — a walk, feeding, medication dose, or vet appointment. It stores the task title, type, duration, priority level, scheduled time, and completion status. Its responsibility is to model a single schedulable event with enough information for the Scheduler to sort and explain it. It was also implemented as a dataclass, with `completed` defaulting to `False` so every new task starts as pending.

**Scheduler** is the logic layer. It takes an Owner, filters each pet's tasks down to those due today, and sorts them by priority and time into an ordered plan. Its responsibility is entirely algorithmic — it does not store data permanently, only produces and exposes a plan for a given day. It was implemented as a regular class because its constructor takes behavioral arguments rather than purely describing data.

**b. Design changes**

Yes, the design changed in one significant way during implementation. The original `Scheduler` skeleton was designed to take a single `Pet` and a target `date` as its constructor arguments. This made sense early on when the system only had one pet in mind. However, once the requirement became "view today's tasks across all pets," passing a single `Pet` was no longer enough — the Scheduler would have needed to be created and run separately for each pet, then the results manually merged.

The change was to pass `Owner` into the `Scheduler` instead. This allowed the scheduler to loop across `owner.get_pets()` and collect tasks from every pet into one flat list before sorting. The result is a single unified plan that naturally spans multiple pets, which is what an owner actually needs each morning. The relationship in the UML was updated to reflect this — `Scheduler --> Owner` instead of `Scheduler --> Pet`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints when building a daily plan:

1. **Priority level** is the most important rule. A high priority task will always show up before medium or low tasks no matter what time it is supposed to happen. We set it up this way so that crucial things like giving medication never get lost under everyday chores.

2. **Scheduled time** works as a tiebreaker when tasks have the exact same priority. This means the earlier task will be listed first to keep the plan easy to read.

3. **Time window overlap** is when the app checks if the times for any tasks clash with each other. It will give you a warning instead of blocking you from making the plan.

We made priority the main rule because missing an important medication is much worse than skipping a normal walk. We chose to use warnings for schedule conflicts instead of stopping you completely because real life gets messy, and the owner should always remain in control.

**b. Tradeoffs**

The scheduler sorts tasks by priority first and then by time. This means a high priority task at 6 PM will always show up before a medium priority task at 7 AM, even if the morning task actually happens first in the real world. We made this choice on purpose because urgency matters more than the clock in a pet care app. Missing a medication is much worse than missing a walk. The app also has a second feature that sorts tasks strictly by time, so the owner can easily see what is most critical along with what is coming up next. Most users need both options, and separating them into two views is much clearer than trying to combine priority and time into a single opinionated sort.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used throughout every phase of the project, but the role it played changed depending on the task:

- **Design brainstorming** — In the early phases, AI was used as a sounding board to identify which classes were needed, what attributes each should hold, and how they should relate to each other. Asking "what are the most important edge cases for a pet scheduler?" produced a useful list that directly shaped the test plan.

- **Scaffolding** — AI generated the initial class skeletons (method stubs with `pass`) from the UML description. This saved time and meant the structure was consistent with the design before any logic was written.

- **Algorithm implementation** — AI drafted the sorting key, the interval intersection conflict detection formula (`A.start < B.end AND B.start < A.end`), the `timedelta`-based recurrence logic, and the session state pattern for Streamlit persistence.

- **Test generation** — After the core logic was complete, AI drafted the 16-test suite covering happy paths and edge cases across all four feature areas.

- **Debugging** — When the "Mark done" button caused the schedule to disappear on rerun, AI diagnosed the root cause (the plan was not persisted in `st.session_state`) and proposed the fix.

The most effective prompts were specific and grounded in the actual code — for example, referencing the file directly and asking a focused question like "how should the Scheduler retrieve all tasks from the Owner's pets?" rather than asking for a complete implementation up front.

**b. Judgment and verification**

The clearest moment of overriding an AI suggestion came during the `Scheduler` design. The initial scaffold gave `Scheduler` a constructor of `__init__(self, pet: Pet, date: date)` — one pet, one date. AI generated this because the UML at that point showed a direct `Scheduler --> Pet` relationship, which was correct for a single-pet system.

When it became clear the app needed to schedule across multiple pets owned by one person, accepting that scaffold as-is would have meant either duplicating the scheduler per pet or adding an awkward loop outside the class. Instead, the decision was made to change the constructor to `__init__(self, owner: Owner)` and move the cross-pet traversal inside `build_plan()`. This kept the scheduling logic self-contained and made the external interface much simpler — one scheduler per owner, not one per pet.

The verification was straightforward: the `main.py` CLI demo was run with two pets and tasks assigned to both. If the output showed tasks from both pets in a single sorted plan, the design worked. It did, and the UML was updated to match.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers four areas:

1. **Sorting correctness** — tasks added to a pet out of chronological order must come back sorted correctly by `get_tasks_by_time()`. A separate test confirms that high priority always ranks above low priority regardless of scheduled time, and a third confirms that time is used as a tiebreaker within the same priority group. These tests matter because the sorting logic is the core value the scheduler provides — if it returns tasks in the wrong order, the whole system is unreliable.

2. **Recurrence logic** — completing a `daily` task must create a new task with `scheduled_time` exactly one day later; a `weekly` task must land exactly seven days out; a `none` task must not create any new entry. These are tested because a bug here would be invisible to the user until they noticed a medication reminder silently stopped appearing.

3. **Conflict detection** — overlapping time windows must be caught, non-overlapping windows must produce no conflicts, and two tasks at the exact same start time must always be flagged. These tests matter because a silent conflict means an owner might schedule two things at the same time without realizing it.

4. **Edge cases** — a pet with no tasks, an owner with no pets, filtering by pet name, and hiding completed tasks. These tests prevent crashes from empty state and confirm the filtering logic excludes the right data.

**b. Confidence**

Confidence level: **4 out of 5**.

All 16 tests pass and the core behaviors are well covered. The one area of lower confidence is data persistence — because tasks reset on every browser refresh, there is no way to test long-running recurrence behavior (for example, whether a daily task chains correctly over multiple real days). The conflict detection algorithm is also O(n²), which works fine for a typical pet care schedule of 10–20 tasks per day but has not been tested under load. If given more time, the next tests would be: a simulation of completing a recurring task seven days in a row to verify the chain, and a stress test with 50+ tasks to check that conflict detection stays fast.

---

## 5. Reflection

**a. What went well**

The part of the project I am most satisfied with is the CLI-first workflow. By building and verifying `pawpal_system.py` entirely through `main.py` before touching the Streamlit UI, every method was proven to work in isolation. When it came time to wire the UI, the only problems were Streamlit-specific (session state, reruns) — the backend logic itself never needed to be revisited. That clean separation made debugging much faster and gave a high degree of confidence in the system before the first button was ever clicked in a browser.

**b. What you would improve**

In a second iteration, the first priority would be data persistence. Resetting to zero on every browser refresh is the most significant limitation of the current app for real-world use. Saving the owner, pets, and tasks to a local SQLite database using Python's built-in `sqlite3` module would solve this without adding external dependencies. The second improvement would be replacing the O(n²) conflict detection with a sweep-line algorithm that sorts tasks by start time first and only checks adjacent windows — this would scale much better for owners with many pets and dense schedules.

**c. Key takeaway**

The most important thing this project taught me is that AI is a powerful accelerator, but it requires a human to act as the lead architect at every step. AI can generate correct code very quickly, but it generates code that fits the description it was given — it does not know what the system is supposed to feel like from the user's perspective, or when a technically valid design creates an awkward interface. The decision to move `Owner` into `Scheduler` instead of `Pet` is a good example: AI had no reason to suggest it because both designs compile and run. Recognizing which design was actually better required understanding the use case, stepping back from the generated code, and making a judgment call. That judgment — not the code generation — is where the real engineering happens.
