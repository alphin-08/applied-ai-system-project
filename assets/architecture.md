# PawPal+ System Architecture

## RAG-Enhanced Pet Care Scheduler

```mermaid
flowchart TD
    %% ── INPUT ───────────────────────────────────────────────────────────────
    USER(["👤 User\n─────────────────\nPet name, species, age\nHealth notes, tasks\nScheduled times"])

    %% ── STREAMLIT UI ─────────────────────────────────────────────────────────
    subgraph UI["Streamlit UI  (app.py)"]
        REG["Pet Registration\n+ Task Entry Form"]
        BTN["'Build Schedule' Button"]
    end

    %% ── CORE SCHEDULER ───────────────────────────────────────────────────────
    subgraph CORE["Core Scheduler  (pawpal_system.py)"]
        SCHED["Scheduler\n─────────────────\nPriority sort · Conflict detection\nRecurrence expansion"]
    end

    %% ── RAG PIPELINE ─────────────────────────────────────────────────────────
    subgraph RAG["RAG Pipeline  (retriever.py + pet_care_kb.py + ai_advisor.py)"]
        KB[("Pet Care Knowledge Base\n─────────────────────────────\nFeeding guidelines by species\nExercise needs by age\nMedication handling tips\nHealth-condition warnings")]
        RET["Retriever\n─────────────────\nMatches pet profile + task types\nto relevant KB sections"]
        LLM["Gemini AI  (gemini-2.5-flash)\n─────────────────\nReceives: schedule + retrieved\nguidelines + pet profile\nOutputs: personalised care advice"]
    end

    %% ── OUTPUT ───────────────────────────────────────────────────────────────
    subgraph OUT["Output Display  (Streamlit)"]
        PLAN["Prioritised Schedule\nConflict warnings"]
        ADVICE["AI Care Summary\nPersonalised recommendations"]
    end

    %% ── VALIDATION ───────────────────────────────────────────────────────────
    subgraph VAL["Validation"]
        HUMAN(["👤 Human Review\nUser reads AI advice\nMarks tasks complete"])
        TESTS["Test Suite\n(tests/test_pawpal.py · tests/smoke_test.py)\n─────────────────────\nVerifies: sort order\nconflict detection\nrecurrence logic\nfull RAG pipeline"]
    end

    %% ── DATA FLOW ────────────────────────────────────────────────────────────
    USER        --> REG
    REG         --> BTN
    BTN         --> SCHED
    BTN         --> RET
    KB          --> RET
    SCHED       --> PLAN
    SCHED       --> LLM
    RET         --> LLM
    LLM         --> ADVICE
    PLAN        --> HUMAN
    ADVICE      --> HUMAN
    TESTS       -.->|validates| SCHED
    TESTS       -.->|validates| LLM
```

---

## Component Descriptions

| Component | File | Role |
|---|---|---|
| **Streamlit UI** | `app.py` | Collects pet profiles and tasks; renders the final schedule and AI advice |
| **Scheduler** | `pawpal_system.py` | Sorts tasks by priority + time, detects time-window conflicts, expands recurrences |
| **Pet Care Knowledge Base** | `pet_care_kb.py` | Static guidelines organised by species, age, task type, and health condition |
| **Retriever** | `retriever.py` | Keyword-matches the pet's profile and task types against the KB; returns the most relevant sections |
| **Gemini AI** | `ai_advisor.py` | Combines the retrieved guidelines with the built schedule to produce personalised care advice |
| **Human Review** | — | User validates AI recommendations and marks tasks done — closes the feedback loop |
| **Test Suite** | `tests/` | `test_pawpal.py` verifies scheduler logic; `smoke_test.py` validates the full RAG + AI pipeline end-to-end |

---

## Data Flow Summary

```
User Input
  └─► Streamlit UI
        ├─► Scheduler ──────────────────────────────► Prioritised Schedule ─┐
        └─► Retriever ◄── Knowledge Base                                     ├─► Human Review
              └─► Gemini AI (schedule + guidelines) ► AI Care Summary ───────┘
                                                                              ▲
                                          Test Suite ──── validates ──► Scheduler + AI layer
```
