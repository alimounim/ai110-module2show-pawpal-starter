from pawpal_system import Task, Pet, Owner, Scheduler

# --- Create Owner ---
owner = Owner(name="Alex", email="alex@example.com", time_available_per_day=2.0)

# --- Create Pets ---
buddy = Pet(name="Buddy", specie="Dog", age=3, weight=12.5, health_notes="Allergic to grain")
whiskers = Pet(name="Whiskers", specie="Cat", age=5, weight=4.2)

# --- Add Tasks OUT OF ORDER (intentionally scrambled times) ---
buddy.add_task(Task(name="Evening Walk",    category="Exercise", duration_minutes=30, priority="medium", frequency="daily",   scheduled_time="18:00"))
buddy.add_task(Task(name="Feed Breakfast",  category="Feeding",  duration_minutes=10, priority="high",   frequency="daily",   scheduled_time="07:30"))
buddy.add_task(Task(name="Morning Walk",    category="Exercise", duration_minutes=30, priority="high",   frequency="daily",   scheduled_time="08:00"))
# HARD conflict: Buddy has two tasks starting at 08:00 (Morning Walk runs until 08:30, Grooming starts 08:15)
buddy.add_task(Task(name="Grooming",        category="Grooming", duration_minutes=20, priority="low",    frequency="weekly",  scheduled_time="08:15"))

whiskers.add_task(Task(name="Clean Litter Box", category="Hygiene",  duration_minutes=5,  priority="medium", frequency="daily",   scheduled_time="09:00"))
whiskers.add_task(Task(name="Vet Checkup",       category="Health",   duration_minutes=60, priority="high",   frequency="monthly", scheduled_time="14:00"))
whiskers.add_task(Task(name="Brushing",          category="Grooming", duration_minutes=15, priority="low",    frequency="weekly",  scheduled_time="11:30"))
# SOFT conflict: Buddy's Evening Walk (18:00–18:30) overlaps Whiskers' Dinner (18:20)
whiskers.add_task(Task(name="Dinner",            category="Feeding",  duration_minutes=10, priority="high",   frequency="daily",   scheduled_time="18:20"))

# (tasks marked complete via scheduler after setup — see recurring demo below)

# --- Register Pets with Owner ---
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Run Scheduler ---
scheduler = Scheduler(owner)
scheduler.display_schedule()

# --- Extra info ---
print(f"\nFits in today's available time: {'Yes' if scheduler.fits_in_schedule() else 'No'}")
print(f"\nHigh priority tasks:")
for pet, task in scheduler.get_tasks_by_priority("high"):
    print(f"  - [{pet.name}] {task.name} ({task.duration_minutes} min)")

# ── Recurring task demo ───────────────────────────────────────────────────────
print("\n=== Completing 'Feed Breakfast' (daily) via scheduler ===")
feed_task = buddy.tasks[1]  # Feed Breakfast
new_task = scheduler.complete_task(buddy, feed_task)
print(f"  Original : '{feed_task.name}' completed={feed_task.completed}, last_completed={feed_task.last_completed_date}")
print(f"  New copy : '{new_task.name}' completed={new_task.completed}, last_completed={new_task.last_completed_date}")
print(f"  Buddy now has {len(buddy.tasks)} tasks (was 3)")

print("\n=== Completing 'Vet Checkup' (monthly) — no recurrence expected ===")
vet_task = whiskers.tasks[1]
result = scheduler.complete_task(whiskers, vet_task)
print(f"  New copy created: {result is not None}")  # False — monthly doesn't recur
print(f"  Whiskers still has {len(whiskers.tasks)} tasks")

# ── Sorting demo ──────────────────────────────────────────────────────────────
print("\n=== All Tasks Sorted by Time ===")
for pet, task in scheduler.sort_by_time():
    status = "[x]" if task.completed else "[ ]"
    print(f"  {status} {task.scheduled_time}  [{pet.name}] {task.name} — {task.duration_minutes} min")

# ── Filtering demos ───────────────────────────────────────────────────────────
print("\n=== Pending Tasks Only ===")
for pet, task in scheduler.filter_tasks(completed=False):
    print(f"  [ ] [{pet.name}] {task.name} @ {task.scheduled_time}")

print("\n=== Completed Tasks Only ===")
for pet, task in scheduler.filter_tasks(completed=True):
    print(f"  [x] [{pet.name}] {task.name} @ {task.scheduled_time}")

print("\n=== Buddy's Tasks Only ===")
for pet, task in scheduler.filter_tasks(pet_name="Buddy"):
    status = "[x]" if task.completed else "[ ]"
    print(f"  {status} {task.name} @ {task.scheduled_time}")

print("\n=== Whiskers' Pending Tasks ===")
for pet, task in scheduler.filter_tasks(pet_name="Whiskers", completed=False):
    print(f"  [ ] {task.name} @ {task.scheduled_time}")

# ── Conflict detection demo ───────────────────────────────────────────────────
print("\n=== Conflict Detection ===")
conflicts = scheduler.get_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  ⚠  {warning}")
else:
    print("  No conflicts found.")
