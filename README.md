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

## Smarter Scheduling

The `Scheduler` class goes beyond a simple task list with several intelligent features:

- **Conflict detection** — `get_conflicts()` checks all pending tasks for overlapping time windows. Same-pet overlaps are flagged as `[HARD CONFLICT]` (one body, one owner); cross-pet overlaps are flagged as `[SOFT CONFLICT]` (potentially manageable).
- **Time-sorted view** — `sort_by_time()` returns all tasks ordered by `scheduled_time` (HH:MM), making it easy to render a chronological daily plan.
- **Flexible filtering** — `filter_tasks(pet_name, completed)` lets the UI show only a specific pet's tasks or only pending/completed items without fetching everything.
- **Capacity check** — `fits_in_schedule()` compares the total minutes of all daily-frequency tasks against the owner's available hours, flagging over-scheduled days before they happen.
- **Auto-recurrence** — `complete_task()` marks a task done and automatically enqueues a fresh copy for `daily` and `weekly` tasks, so recurring care never falls off the list.
