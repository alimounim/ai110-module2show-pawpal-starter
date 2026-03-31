from pawpal_system import Task, Pet, Owner, Scheduler

# --- Create Owner ---
owner = Owner(name="Alex", email="alex@example.com", time_available_per_day=2.0)

# --- Create Pets ---
buddy = Pet(name="Buddy", specie="Dog", age=3, weight=12.5, health_notes="Allergic to grain")
whiskers = Pet(name="Whiskers", specie="Cat", age=5, weight=4.2)

# --- Add Tasks to Buddy ---
buddy.add_task(Task(name="Morning Walk", category="Exercise", duration_minutes=30, priority="high", frequency="daily"))
buddy.add_task(Task(name="Feed Breakfast", category="Feeding", duration_minutes=10, priority="high", frequency="daily"))

# --- Add Tasks to Whiskers ---
whiskers.add_task(Task(name="Clean Litter Box", category="Hygiene", duration_minutes=5, priority="medium", frequency="daily"))
whiskers.add_task(Task(name="Brushing", category="Grooming", duration_minutes=15, priority="low", frequency="weekly"))
whiskers.add_task(Task(name="Vet Checkup", category="Health", duration_minutes=60, priority="high", frequency="monthly"))

# --- Register Pets with Owner ---
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Run Scheduler ---
scheduler = Scheduler(owner)
scheduler.display_schedule()

# --- Extra info ---
print(f"\nFits in today's available time: {'Yes' if scheduler.fits_in_schedule() else 'No'}")
print(f"High priority tasks today:")
for pet, task in scheduler.get_tasks_by_priority("high"):
    print(f"  - [{pet.name}] {task.name} ({task.duration_minutes} min)")
