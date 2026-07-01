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

## 🖥️ Sample Output

```
08:00-09:00
  • Morning walk [HIGH, 30 min] — Rex (dog)
  • Feed breakfast [HIGH, 15 min] — Milo (cat)
  • Litter cleanup [LOW, 10 min] — Milo (cat)
  (5 min free)
18:00-19:00
  • Evening walk [MEDIUM, 30 min] — Rex (dog)
  (30 min free)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The scheduler reasons about two core constraints — **time capacity** and **priority** — and layers sorting, filtering, conflict detection, and recurrence on top.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts all tasks by `scheduled_start` (as an `"HH:MM"` key); unscheduled tasks sort last via a `"99:99"` sentinel. |
| Priority-first placement | `Scheduler.auto_assign()` | Greedy first-fit: sorts pending tasks `HIGH → MEDIUM → LOW`, then drops each into the first window with remaining capacity. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.pending_tasks()` | `filter_tasks` narrows by completion status and/or pet name; `pending_tasks` skips tasks that are completed or already scheduled. Placement stops for a task when no window has capacity. |
| Conflict handling | `Scheduler.detect_conflicts()` | Sorts occurrences by start time and sweeps once, reporting any `[start, end)` intervals that overlap (back-to-back tasks don't conflict). Detects, does not prevent. |
| Recurring tasks | `Scheduler.complete_task()`, `Scheduler._next_occurrence()` | On completion, spawns the next occurrence based on `Task.frequency` (ONCE / DAILY / WEEKLY / MONTHLY); MONTHLY clamps to the last valid day of the month. |
| Rescheduling | `Scheduler.reschedule()` | Drops all incomplete assignments and re-runs `auto_assign()` from scratch. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
