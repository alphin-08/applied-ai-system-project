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

**Scheduler** is the logic layer. It takes a Pet and a target date, filters the pet's tasks down to those due that day, and sorts them by priority and time into an ordered plan. Its responsibility is entirely algorithmic — it does not store data permanently, only produces and exposes a plan for a given day. It was implemented as a regular class because its constructor takes behavioral arguments (a pet and a date) rather than purely describing data.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints when building a daily plan:

1. **Priority level** (`high`, `medium`, `low`) — the most heavily weighted constraint. A high-priority task always appears before medium or low tasks regardless of when it is scheduled on the clock. This ensures critical care like medication is never buried under routine tasks.

2. **Scheduled time** — used as a tiebreaker within the same priority group. If two high-priority tasks exist, the one scheduled earlier in the day appears first, keeping the plan naturally readable.

3. **Time window overlap** — the scheduler checks whether any two tasks' start-to-end windows intersect using interval intersection logic. It does not block the plan, but surfaces a warning so the owner can decide how to resolve it.

Priority was chosen as the dominant constraint because the core risk in pet care is missing something critical — a missed medication is far more consequential than a missed walk. Conflict detection was kept as a warning rather than a hard block to avoid making the app frustrating; real-life schedules are messy and the owner should stay in control.

**b. Tradeoffs**

The scheduler sorts tasks by priority first and then by time. This means a high priority task at 6 PM will always show up before a medium priority task at 7 AM, even if the morning task actually happens first in the real world. We made this choice on purpose because urgency matters more than the clock in a pet care app. Missing a medication is much worse than missing a walk. The app also has a second feature that sorts tasks strictly by time, so the owner can easily see what is most critical along with what is coming up next. Most users need both options, and separating them into two lists is much clearer than trying to mix priority and time together.

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
