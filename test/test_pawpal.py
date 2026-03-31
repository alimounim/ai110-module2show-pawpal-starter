from pawpal_system import Task, Pet


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
