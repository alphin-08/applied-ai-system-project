# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform in PawPal+:

1. **Add a pet** — The user registers a pet by providing its name, species, age, and any special health notes. This creates a profile that all future tasks and schedules are tied to, making it the foundation of the entire system.

2. **Schedule a care task** — The user creates a task for a specific pet (such as a walk, feeding, medication dose, or vet appointment), setting a date, time, and priority level. This is the primary daily interaction — building out the pet's care calendar.

3. **View today's tasks** — The user sees a prioritized list of all care tasks due today across all their pets. The system sorts tasks by urgency and type so the owner always knows what needs attention first.

The three main objects and their responsibilities:

**Pet**
- Attributes: `name` (str), `species` (str), `age` (int), `health_notes` (str), `tasks` (list of CareTask)
- Methods: `add_task(task)` — attaches a CareTask to this pet; `get_tasks()` — returns all tasks for this pet

**CareTask**
- Attributes: `title` (str), `task_type` (str: "walk" | "feeding" | "medication" | "appointment"), `duration_minutes` (int), `priority` (str: "low" | "medium" | "high"), `scheduled_time` (datetime), `completed` (bool)
- Methods: `mark_complete()` — flips `completed` to True; `is_due_today()` — checks if `scheduled_time` falls on today's date; `__repr__()` — returns a readable summary string

**Scheduler**
- Attributes: `pet` (Pet), `date` (date), `plan` (list of CareTask)
- Methods: `build_plan()` — filters today's tasks and sorts them by priority then time; `get_next_task()` — returns the top incomplete task; `explain_plan()` — returns a human-readable string describing the ordered schedule and why each task was placed where it was

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
