# Applied AI System: PawPal+ with a Reliability Layer

## Base project
Original project: **PawPal+** (Module 2). It was a pet care scheduling app built with
Python OOP (`Task`, `Pet`, `Owner`, `Scheduler`) and a Streamlit UI. It sorted tasks by
time, filtered by pet and status, warned about scheduling conflicts, and created
recurring daily and weekly tasks.

## What this adds
- `validation.py`: guardrails that reject bad times, frequencies, and descriptions, and
  log accepted and rejected input to `pawpal.log`. The Streamlit app uses it for every
  new task, so bad input becomes a warning instead of bad data.
- `evaluate.py`: a harness that runs 20 predefined checks (including 40 seeded random
  tasks across two pets) and writes a pass/fail table to `logs/evaluation_report.md`.
- `test_guardrails.py`: 5 pytest tests for the guardrails.

## Architecture
The diagram is in `diagrams/architecture.mmd`. User input goes through
`validation.make_task`, which either rejects it (a warning shown and logged) or builds a
`Task` that is added to a `Pet`. The `Scheduler` then sorts, filters, detects conflicts,
and handles recurrence across all pets. `evaluate.py` drives the same validation and
scheduler code and writes a pass/fail report for human review.

## Setup
```
python -m pip install -r requirements.txt
python main.py
python evaluate.py
python -m pytest
python -m streamlit run app.py
```

## Sample interactions

CLI demo:
```
$ python main.py

Today's Schedule (sorted by time)
---------------------------------
  [ ] 08:00  Buddy  Breakfast (daily, 2026-11-22)
  [ ] 08:00  Mimi   Medication (once, 2026-11-22)
  [ ] 13:30  Mimi   Vet appointment (once, 2026-11-22)
  [ ] 18:00  Buddy  Evening walk (daily, 2026-11-22)

Conflict check
--------------
  WARNING: conflict on 2026-11-22 at 08:00 -> Buddy: Breakfast, Mimi: Medication

Filter: Mimi's tasks
--------------------
  [ ] 08:00  Mimi   Medication (once, 2026-11-22)
  [ ] 13:30  Mimi   Vet appointment (once, 2026-11-22)

Completing 'Breakfast' (daily) ...
  Next occurrence created for 2026-11-23 at 08:00

Filter: completed tasks
-----------------------
  [x] 08:00  Buddy  Breakfast (daily, 2026-11-22)

Filter: Buddy's pending tasks
-----------------------------
  [ ] 18:00  Buddy  Evening walk (daily, 2026-11-22)
  [ ] 08:00  Buddy  Breakfast (daily, 2026-11-23)
```

Evaluation harness (guardrails and scheduler):
```
$ python evaluate.py
[PASS] time '25:00' rejected: expected 'rejected', got 'rejected'
[PASS] time '9:5' rejected: expected 'rejected', got 'rejected'
[PASS] description '' (len 0) rejected: expected 'rejected', got 'rejected'
[PASS] frequency 'hourly' rejected: expected 'rejected', got 'rejected'
[PASS] time '09:05' accepted: expected 'accepted', got 'accepted'
[PASS] 40 random tasks across 2 pets sort chronologically: expected True, got True
[PASS] one cross-pet conflict detected: expected 1, got 1
[PASS] daily task recurs 1 day later: expected 1, got 1
[PASS] one-time task does not recur: expected None, got None
...
Summary: 20/20 checks passed
```
(The full list of 20 checks is in `logs/evaluation_report.md`.)

Live app log (`pawpal.log`), from adding one valid task and one empty one in the Streamlit app:
```
2026-11-22 22:10:03,934 INFO Created task 'Fetching a stick' at 00:45 (once)
2026-11-22 22:10:20,390 WARNING Rejected task '' at '22:09': Description cannot be empty.
```

## Guardrail examples
| Input | Behavior | Result |
|---|---|---|
| Time `25:00` | rejected | `Time must be HH:MM in 24-hour format, got '25:00'.` |
| Time `9:5` | rejected | `Time must be HH:MM in 24-hour format, got '9:5'.` |
| Empty description | rejected | `Description cannot be empty.` |
| 200-character description | rejected | `Description must be 80 characters or fewer.` |
| Frequency `hourly` | rejected | `Frequency must be one of ('once', 'daily', 'weekly'), got 'hourly'.` |
| Two tasks at 08:00 | conflict warning, no crash | `WARNING: conflict on ...` from `detect_conflicts()` |

## Design decisions
Validation lives in its own module so the UI, the tests, and the harness share the same
rules and I didn't have to change the original core classes. Conflicts return warnings
instead of raising errors. Trade-off: only exact time matches are flagged, not
overlapping durations.

## Testing summary
`python evaluate.py`: 20/20 checks passed. `python -m pytest`: 14 passed (9 original
PawPal+ tests plus 5 guardrail tests). The live app logged both an accepted and a
rejected task.

## Reflection
This project showed me that a feature isn't done when it works once. Writing the
harness forced me to define what "correct" means for bad input, not just good input.

# 🐾 PawPal+

PawPal+ is a pet care scheduling app. Owners add pets, schedule care tasks (feedings, walks, medications, appointments), and get a sorted schedule with conflict warnings and automatic recurring tasks.

## System Overview

| Class | Responsibility |
|-------|----------------|
| `Task` | One activity: description, time (`HH:MM`), frequency, due date, completion status. Can `mark_complete()` and create its `next_occurrence()`. |
| `Pet` | Pet details plus its list of tasks (`add_task`, `remove_task`, `list_tasks`). |
| `Owner` | Owner details and a list of pets; can gather all tasks across pets. |
| `Scheduler` | The "brain": retrieves, sorts, filters, and manages tasks across all of an owner's pets. |

UML diagrams: `diagrams/uml_draft.mmd` (initial) and `diagrams/uml_final.mmd` (matches final code).

## Features

- **Sorting by time:** `Scheduler.sort_by_time()` orders tasks by due date, then `HH:MM`.
- **Filtering:** `Scheduler.filter_tasks(pet_name, completed)` filters by pet and/or completion status.
- **Conflict detection:** `Scheduler.detect_conflicts()` returns warning messages when incomplete tasks share the same date and time (same or different pets). It warns instead of crashing.
- **Recurring tasks:** `Scheduler.mark_task_complete()` completes a task and, for `daily` or `weekly` tasks, adds the next occurrence using `timedelta` (today + 1 or + 7 days).
- **Today's schedule:** `Scheduler.todays_schedule()` returns today's pending tasks in time order.

## Smarter Scheduling

| Feature | Method | Behavior |
|---------|--------|----------|
| Sorting | `Scheduler.sort_by_time()` | Chronological by `(due_date, time)` across all pets |
| Filtering | `Scheduler.filter_tasks()` | By pet name, completion status, or both |
| Conflict detection | `Scheduler.detect_conflicts()` | Exact date + time matches among incomplete tasks; returns warning strings |
| Recurring tasks | `Scheduler.mark_task_complete()` / `Task.next_occurrence()` | Daily creates tomorrow's task, weekly creates next week's |

## Demo Walkthrough

**UI features (Streamlit):** set the owner name, add pets, schedule tasks (pet, description, time, frequency), filter by pet or status, mark tasks complete.

**Example workflow:** add a pet (Buddy) → schedule "Breakfast" at 08:00 daily → schedule "Medication" for another pet at 08:00 → the schedule appears sorted by time with a conflict warning → mark Breakfast complete → tomorrow's Breakfast is created automatically.

**Key Scheduler behaviors shown:** sorting by time, conflict warnings (`st.warning`), filtering, and recurring task creation.

### Sample Output

Run `python main.py`:

```

Today's Schedule (sorted by time)
---------------------------------
  [ ] 08:00  Buddy  Breakfast (daily, 2026-11-01)
  [ ] 08:00  Mimi   Medication (once, 2026-11-01)
  [ ] 13:30  Mimi   Vet appointment (once, 2026-11-01)
  [ ] 18:00  Buddy  Evening walk (daily, 2026-11-01)

Conflict check
--------------
  WARNING: conflict on 2026-11-01 at 08:00 -> Buddy: Breakfast, Mimi: Medication

Filter: Mimi's tasks
--------------------
  [ ] 08:00  Mimi   Medication (once, 2026-11-01)
  [ ] 13:30  Mimi   Vet appointment (once, 2026-11-01)

Completing 'Breakfast' (daily) ...
  Next occurrence created for 2026-11-02 at 08:00

Filter: completed tasks
-----------------------
  [x] 08:00  Buddy  Breakfast (daily, 2026-11-01)

Filter: Buddy's pending tasks
-----------------------------
  [ ] 18:00  Buddy  Evening walk (daily, 2026-11-01)
  [ ] 08:00  Buddy  Breakfast (daily, 2026-11-02)
```

## Getting Started

```bash
pip install -r requirements.txt
python main.py            # CLI demo
streamlit run app.py      # web app
python -m pytest          # run tests
```

## Testing PawPal+

Command: `python -m pytest`

Tests (in `tests/test_pawpal.py`) cover:
- Task completion changes status
- Adding tasks increases a pet's task count
- Sorting returns chronological order across multiple pets
- Daily recurrence creates a next-day task; one-time tasks do not recur
- Conflict detection flags duplicate times and stays quiet otherwise
- Edge cases: a pet with no tasks, filtering by pet and status

Test output:

```
=================================================== test session starts ====================================================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\rleyv\applied-ai-system\applied-ai-system-final
plugins: anyio-4.15.1
collected 14 items                                                                                                          

test_guardrails.py .....                                                                                              [ 35%]
test_pawpal.py .........                                                                                              [100%]

==================================================== 14 passed in 0.16s ====================================================
```

**Confidence Level:** ⭐⭐⭐⭐ (4/5). Core behaviors and key edge cases pass; overlapping durations and time-zone handling are not covered.
