from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False

    def edit(self, **kwargs) -> None:
        """Update one or more task fields by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    specie: str
    age: int
    weight: float
    health_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def get_careplan(self) -> dict:
        """Return a dictionary summary of this pet's info and all its tasks."""
        return {
            "pet": self.name,
            "specie": self.specie,
            "age": self.age,
            "weight": self.weight,
            "health_notes": self.health_notes,
            "tasks": [
                {
                    "name": t.name,
                    "category": t.category,
                    "duration_minutes": t.duration_minutes,
                    "priority": t.priority,
                    "frequency": t.frequency,
                    "completed": t.completed,
                }
                for t in self.tasks
            ],
        }

    def update_info(self, **kwargs) -> None:
        """Update one or more pet fields by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Owner:
    def __init__(self, name: str, email: str, time_available_per_day: float):
        self.name = name
        self.email = email
        self.time_available_per_day = time_available_per_day
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pet list."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all tasks across all pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The brain — retrieves, organizes, and manages tasks across all pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every pet the owner has."""
        return self.owner.get_all_tasks()

    def get_tasks_by_priority(self, priority: str) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs whose task matches the given priority."""
        return [(pet, task) for pet, task in self.get_all_tasks() if task.priority == priority]

    def get_tasks_by_frequency(self, frequency: str) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs whose task matches the given frequency."""
        return [(pet, task) for pet, task in self.get_all_tasks() if task.frequency == frequency]

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs where the task has not yet been completed."""
        return [(pet, task) for pet, task in self.get_all_tasks() if not task.completed]

    def get_completed_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs where the task has been completed."""
        return [(pet, task) for pet, task in self.get_all_tasks() if task.completed]

    def total_daily_minutes(self) -> float:
        """Sum the duration of all daily-frequency tasks across all pets."""
        return sum(task.duration_minutes for _, task in self.get_tasks_by_frequency("daily"))

    def fits_in_schedule(self) -> bool:
        """Return True if total daily task time fits within the owner's available hours."""
        return self.total_daily_minutes() <= self.owner.time_available_per_day * 60

    def display_schedule(self) -> None:
        """Print all pending tasks and daily time usage to the console."""
        print(f"\n=== Schedule for {self.owner.name} ({date.today()}) ===")
        for pet, task in self.get_pending_tasks():
            status = "[x]" if task.completed else "[ ]"
            print(f"  {status} [{pet.name}] {task.name} — {task.duration_minutes} min ({task.priority} priority, {task.frequency})")
        daily_mins = self.total_daily_minutes()
        available_mins = self.owner.time_available_per_day * 60
        print(f"\nDaily tasks: {daily_mins} min / {available_mins:.0f} min available")
