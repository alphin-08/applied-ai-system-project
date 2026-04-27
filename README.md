# PawPal+

A smart, AI-powered pet care scheduling app built with Python and Streamlit.

Link to Demo: https://www.loom.com/share/994bcff111974d6796f09161929fcac4

---

## Original Project (Modules 1–3): PawPal+

PawPal started as a basic scheduling system without any AI. The main goal was to let owners add multiple pets, assign daily tasks, and get a schedule that avoided time conflicts. The code did three things. It sorted tasks by urgency and time, found overlapping tasks, and automatically created the next task when a repeating one was finished. All the logic was in a single file. I wrote sixteen tests to check the code before building the user interface.

**What It Does Now:**

The app now combines the scheduling engine with a custom database. When you build a schedule, the app pulls specific care facts based on the species, age, and health of the pet. It sends those facts and the schedule to Gemini AI to generate a custom care summary. The AI advice is based entirely on our database instead of generic information. It points out schedule conflicts, gives specific health advice, and warns you if you are missing important care routines.

---

## Features

- **Register multiple pets** — add dogs, cats, or other animals with name, age, species, and health notes, all persisted across interactions via Streamlit session state.
- **Priority-first sorting** — the scheduler ranks tasks `high → medium → low`. A missed medication always appears before a routine walk, regardless of what time either is scheduled.
- **Chronological view** — toggle to a time-sorted view to see tasks in clock order — useful for planning your actual morning routine.
- **Conflict detection** — the scheduler checks every pair of tasks for overlapping time windows using interval intersection logic (`A.start < B.end AND B.start < A.end`). Conflicts surface as visible warnings in the UI.
- **Recurring tasks** — mark a task as `daily` or `weekly`. When you complete it, the next occurrence is automatically created using Python's `timedelta`.
- **Smart filtering** — filter the schedule by a specific pet or hide completed tasks to reduce noise.
- **Mark done in the UI** — each task card has a "Mark done" button that triggers auto-scheduling for recurring tasks on the spot.
- **RAG-powered AI care advice** — after building a schedule, Gemini AI generates a personalised care summary per pet grounded in a curated knowledge base of pet care guidelines.

---

## Architecture Overview

The app is split into three main parts.

**User Interface**, found in app.py. This uses Streamlit to show the website and take your inputs. Clicking the Build Schedule button starts both the scheduler and the AI tools.

**Scheduling Code**, found in pawpal_system.py. These are regular Python classes like Owner, Pet, CareTask, and Scheduler. They work completely on their own without the website or AI. This means I can test the core logic straight from the computer terminal.

**AI Pipeline**, found in pet_care_kb.py, retriever.py, and ai_advisor.py. The database holds specific care rules based on pet type, age, task, and health. The app searches this database for facts that match your pet. It then bundles those facts with your new schedule and sends them to Gemini AI to write the final summary.

See [`assets/architecture.md`](assets/architecture.md) for the full system flowchart and [`assets/class_diagram.mmd`](assets/class_diagram.mmd) for the UML class diagram

---

## Setup Instructions

**1. Clone the repo and create a virtual environment**

```bash
git clone <repo-url>
cd applied-ai-system-project
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your Gemini API key**

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Get a free API key at [ai.google.dev](https://ai.google.dev). Make sure the project you create has **never had billing enabled** to retain free-tier access.

**4. Run the app**

```bash
streamlit run app.py
```

**5. (Optional) Run the CLI demo**

```bash
python main.py
```

**6. (Optional) Run the test suite**

```bash
python -m pytest tests/ -v
```
---

## Sample Interactions

### Example 1 — Young dog with joint issues

**Input:** Mochi, 3yr dog, health notes: "joint stiffness". Tasks: Morning walk (HIGH, 7:00–7:30), Medication (HIGH, 8:00–8:05), Breakfast (HIGH, 8:00–8:15).

**AI Output (excerpt):**

For Mochi's morning walk, it's crucial to ensure it's a short, flat walk to accommodate his joint stiffness, as low-impact exercise is preferred for joint issues. Please avoid stairs, jumping, or rough terrain.

Schedule Conflict Detected: Mochi's 'Medication' (8:00–8:05 AM) and 'Breakfast' (8:00–8:15 AM) are scheduled at the same time. Many medications are best given with food to reduce stomach upset — check the label and adjust timing slightly to complete both tasks effectively.

---

### Example 2 — Senior cat with kidney disease

**Input:** Luna, 12yr cat, health notes: "kidney disease". Tasks: Medication (HIGH, 8:00–8:05), Vet check-up (HIGH, 10:00–11:00).

**AI Output (excerpt):**

Please ensure Luna receives her medication precisely at 8:00 AM. If the medication label advises giving it with food, use a portion of her vet-prescribed low-phosphorus diet to reduce stomach upset.

Before heading to the vet, ensure Luna remains calm — avoid any vigorous activity in the hour prior. It's particularly important to report any sudden changes in her urination frequency, as this is crucial for managing her kidney disease.

---

### Example 3 — Healthy adult dog, no health notes

**Input:** Rex, 5yr dog, no health notes. Tasks: Evening walk (MEDIUM, 6:00–6:45 PM), Dinner (HIGH, 7:00–7:10 PM).

**AI Output (excerpt):**

The schedule correctly places Rex's walk before dinner, avoiding strenuous exercise after a meal and reducing bloat risk. Allow plenty of sniffing time during the walk — mental stimulation reduces anxiety.

Important: The guidelines recommend at least two walks per day for dogs. Rex's schedule only includes one walk today. As an adult dog at peak health, please consider adding a shorter morning walk or extra playtime to ensure adequate exercise and prevent gradual weight gain.

---

## Design Decisions

**Sorting by priority instead of time:**
Urgency matters more than the exact time when you are taking care of pets because missing medicine is much worse than taking a walk a little late. The app has a button that lets owners view tasks in order of time when they need to plan their actual morning routine. I made both views available so you are not forced into using just one specific layout.

**Using warnings instead of blocking conflicts:**
It is common for schedules to change unexpectedly so the app will just warn you if you build a schedule with overlapping tasks instead of completely blocking you from making it. This approach lets the owner decide what to do and keeps the user in full control of their day.

**Using RAG instead of a fine-tuned model:**
A database of care rules is easy to read and update while remaining completely free to use. Training a custom AI model for pet advice would cost money and it would require new training every time the rules change. The current approach gets almost all the same benefits but is much less complicated and allows you to see exactly what facts the AI used to make its choices.

**Giving the scheduler an owner instead of a pet:**
The original code gave a single pet to the scheduler but I changed this to use the owner so the app can look at all the pets and make one combined daily plan. This makes more sense for what a person actually needs every morning and it makes the code simpler because you only need one scheduler for the whole family.

**Using modules instead of classes for the AI tools:**
The retriever and AI advisor files use simple functions instead of full classes because they do not save any data between uses. Every time you run them is a fresh start so writing them as classes would have added a bunch of extra code that the project did not actually need.

---

## Testing Summary

Run the full suite:

```bash
python -m pytest tests/ -v
```

| File | What it covers |
|---|---|
| `tests/test_pawpal.py` | 16 unit tests: priority sorting, chronological sort, conflict detection, recurrence logic, edge cases (empty pets, no tasks, filtering) |
| `tests/smoke_test.py` | End-to-end RAG pipeline across 3 scenarios: young dog with joint issues, senior cat with kidney disease, healthy adult dog |

**All 16 unit tests pass.**

**What worked well:**
Building and testing the core code through the terminal first worked out great. I made sure the main Python file worked completely before I even started on the user interface. This meant I did not have to go back and fix the backend while building the website. The AI pipeline also worked really well and gave accurate advice during my three main tests. It successfully pointed out schedule conflicts and gave good advice based on the specific health conditions of the pets.

**What did not work:**
Figuring out the Gemini API keys was a big problem. The free tier key has to come from a Google Cloud project that has never had billing turned on. If billing is turned on then your free limit drops straight to zero. I also found out that some of the older Gemini models were not available on the free tier for my project, but the newer Gemini 2.5 Flash model worked perfectly fine.

**Confidence level:**
My confidence level for this project is a four out of five. I am very confident in the core scheduling logic because it is fully tested. I am a little less confident in two specific areas. First, the tasks reset whenever you refresh the browser because I did not build a way to save data between sessions. Second, the code that checks for scheduling conflicts might slow down if someone adds a massive list of tasks because I have not stress tested it with a lot of data yet.

---

## Reflection

Building this project taught me that adding AI to an app requires real planning instead of just pasting in some code. The AI tool only works well if the database search works well because the AI will give bad advice if it gets the wrong information. Making the search tool look for the pet species, age, task type, and health all at the same time was the best decision I made. This step is what actually made the final advice feel custom to each pet instead of just sounding like a generic textbook.

My second big lesson was learning how to separate the regular code from the AI tools. Things like finding schedule conflicts, sorting by priority, and repeating tasks all stay in regular Python because that makes them fast and easy to test. The AI is only used to read the database facts and turn them into helpful advice that sounds like a real person wrote it. Keeping these two parts completely separate made the whole project much easier to fix when things broke and made the final app much more reliable.

---
