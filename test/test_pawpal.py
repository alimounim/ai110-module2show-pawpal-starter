from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scheduler(tasks_by_pet: dict[str, list[Task]]) -> tuple[Scheduler, dict[str, Pet]]:
    """Build a Scheduler pre-populated with the given pets and tasks."""
    owner = Owner(name="Alex", email="alex@example.com", time_available_per_day=8)
    pets: dict[str, Pet] = {}
    for pet_name, task_list in tasks_by_pet.items():
        pet = Pet(name=pet_name, specie="dog", age=2, weight=5.0)
        for task in task_list:
            pet.add_task(task)
        owner.add_pet(pet)
        pets[pet_name] = pet
    return Scheduler(owner), pets


# ---------------------------------------------------------------------------
# Existing tests (kept)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(name="Walk", category="exercise", duration_minutes=30, priority="high", frequency="daily")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", specie="dog", age=3, weight=10.5)
    task = Task(name="Feed", category="nutrition", duration_minutes=10, priority="high", frequency="daily")
    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# 1. Sorting Correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """Tasks should come back earliest-to-latest regardless of insertion order."""
    tasks = [
        Task(name="Evening Walk",  category="exercise",   duration_minutes=30, priority="high",   frequency="daily", scheduled_time="18:00"),
        Task(name="Morning Feed",  category="nutrition",  duration_minutes=10, priority="high",   frequency="daily", scheduled_time="07:30"),
        Task(name="Midday Meds",   category="medication", duration_minutes=5,  priority="medium", frequency="daily", scheduled_time="12:00"),
    ]
    scheduler, _ = make_scheduler({"Buddy": tasks})

    sorted_tasks = scheduler.sort_by_time()
    times = [task.scheduled_time for _, task in sorted_tasks]

    assert times == ["07:30", "12:00", "18:00"]


def test_sort_by_time_already_sorted_unchanged():
    """Sorting an already-ordered list should keep the same order."""
    tasks = [
        Task(name="A", category="exercise",  duration_minutes=10, priority="low",  frequency="daily", scheduled_time="08:00"),
        Task(name="B", category="nutrition", duration_minutes=10, priority="high", frequency="daily", scheduled_time="09:00"),
    ]
    scheduler, _ = make_scheduler({"Pet": tasks})

    times = [t.scheduled_time for _, t in scheduler.sort_by_time()]
    assert times == ["08:00", "09:00"]


def test_sort_by_time_empty_returns_empty():
    """A scheduler with no tasks should return an empty sorted list."""
    scheduler, _ = make_scheduler({"EmptyPet": []})
    assert scheduler.sort_by_time() == []


def test_sort_by_time_multiple_pets():
    """Tasks from different pets should be interleaved correctly by time."""
    buddy_tasks = [Task(name="Feed Buddy", category="nutrition", duration_minutes=10, priority="high", frequency="daily", scheduled_time="08:00")]
    max_tasks   = [Task(name="Walk Max",   category="exercise",  duration_minutes=30, priority="high", frequency="daily", scheduled_time="07:00")]
    scheduler, _ = make_scheduler({"Buddy": buddy_tasks, "Max": max_tasks})

    names = [task.name for _, task in scheduler.sort_by_time()]
    assert names == ["Walk Max", "Feed Buddy"]


# ---------------------------------------------------------------------------
# 2. Recurrence Logic
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_new_pending_task():
    """Completing a daily task should add a fresh pending copy to the pet."""
    task = Task(name="Morning Walk", category="exercise", duration_minutes=30, priority="high", frequency="daily")
    scheduler, pets = make_scheduler({"Buddy": [task]})
    pet = pets["Buddy"]

    assert len(pet.tasks) == 1
    scheduler.complete_task(pet, task)

    assert len(pet.tasks) == 2
    new_task = pet.tasks[1]
    assert new_task.completed == False
    assert new_task.last_completed_date is None


def test_complete_weekly_task_creates_new_pending_task():
    """Completing a weekly task should also enqueue a next occurrence."""
    task = Task(name="Bath", category="grooming", duration_minutes=45, priority="medium", frequency="weekly")
    scheduler, pets = make_scheduler({"Luna": [task]})
    pet = pets["Luna"]

    next_task = scheduler.complete_task(pet, task)

    assert next_task is not None
    assert next_task.completed == False
    assert len(pet.tasks) == 2


def test_complete_monthly_task_does_not_create_new_task():
    """Non-recurring frequencies like 'monthly' should NOT spawn a new task."""
    task = Task(name="Vet Visit", category="health", duration_minutes=60, priority="high", frequency="monthly")
    scheduler, pets = make_scheduler({"Buddy": [task]})
    pet = pets["Buddy"]

    result = scheduler.complete_task(pet, task)

    assert result is None
    assert len(pet.tasks) == 1  # original only, no clone
    assert pet.tasks[0].completed == True


def test_complete_task_marks_original_as_done():
    """The original task should be marked complete even when a new one is created."""
    task = Task(name="Feed", category="nutrition", duration_minutes=10, priority="high", frequency="daily")
    scheduler, pets = make_scheduler({"Buddy": [task]})
    pet = pets["Buddy"]

    scheduler.complete_task(pet, task)

    assert pet.tasks[0].completed == True


def test_pet_with_no_tasks_has_empty_pending_list():
    """A pet added with no tasks should contribute nothing to pending tasks."""
    scheduler, _ = make_scheduler({"EmptyPet": []})
    assert scheduler.get_pending_tasks() == []


# ---------------------------------------------------------------------------
# 3. Conflict Detection
# ---------------------------------------------------------------------------

def test_no_conflicts_when_tasks_do_not_overlap():
    """Non-overlapping tasks should produce zero conflict warnings."""
    tasks = [
        Task(name="Feed",  category="nutrition", duration_minutes=10, priority="high", frequency="daily", scheduled_time="08:00"),
        Task(name="Walk",  category="exercise",  duration_minutes=30, priority="high", frequency="daily", scheduled_time="09:00"),
    ]
    scheduler, _ = make_scheduler({"Buddy": tasks})
    assert scheduler.get_conflicts() == []


def test_hard_conflict_same_pet_overlapping_times():
    """Two tasks on the same pet whose windows overlap should produce a HARD conflict."""
    tasks = [
        Task(name="Feed",  category="nutrition", duration_minutes=30, priority="high", frequency="daily", scheduled_time="08:00"),
        Task(name="Meds",  category="medication", duration_minutes=15, priority="high", frequency="daily", scheduled_time="08:15"),
    ]
    scheduler, _ = make_scheduler({"Buddy": tasks})
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) == 1
    assert "HARD" in conflicts[0]


def test_soft_conflict_different_pets_overlapping_times():
    """Two tasks on different pets whose windows overlap should produce a SOFT conflict."""
    buddy_tasks = [Task(name="Walk Buddy", category="exercise", duration_minutes=30, priority="high", frequency="daily", scheduled_time="08:00")]
    max_tasks   = [Task(name="Walk Max",   category="exercise", duration_minutes=30, priority="high", frequency="daily", scheduled_time="08:15")]
    scheduler, _ = make_scheduler({"Buddy": buddy_tasks, "Max": max_tasks})
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) == 1
    assert "SOFT" in conflicts[0]


def test_exact_same_time_same_pet_is_hard_conflict():
    """Two tasks at the exact same time on the same pet should be a HARD conflict."""
    tasks = [
        Task(name="Feed",  category="nutrition", duration_minutes=10, priority="high", frequency="daily", scheduled_time="07:00"),
        Task(name="Brush", category="grooming",  duration_minutes=5,  priority="low",  frequency="daily", scheduled_time="07:00"),
    ]
    scheduler, _ = make_scheduler({"Buddy": tasks})
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) >= 1
    assert all("HARD" in c for c in conflicts)


def test_completed_tasks_excluded_from_conflict_detection():
    """Conflicts should only be detected among pending tasks — completed ones are ignored."""
    done_task    = Task(name="Feed",  category="nutrition", duration_minutes=30, priority="high", frequency="daily", scheduled_time="08:00", completed=True)
    pending_task = Task(name="Meds",  category="medication", duration_minutes=30, priority="high", frequency="daily", scheduled_time="08:00")
    scheduler, _ = make_scheduler({"Buddy": [done_task, pending_task]})

    assert scheduler.get_conflicts() == []


def test_no_conflicts_empty_schedule():
    """An empty schedule should return no conflicts."""
    scheduler, _ = make_scheduler({"EmptyPet": []})
    assert scheduler.get_conflicts() == []
