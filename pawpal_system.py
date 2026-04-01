from dataclasses import dataclass, field, replace
from datetime import date


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False
    scheduled_time: str = "00:00"  # "HH:MM" format, e.g. "08:30"
    last_completed_date: date | None = None

    def edit(self, **kwargs) -> None:
        """Update one or more task fields by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self) -> None:
        """Mark this task as completed and record today's date."""
        self.completed = True
        self.last_completed_date = date.today()


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

    def complete_task(self, pet: Pet, task: Task) -> Task | None:
        """Mark a task complete and automatically enqueue the next occurrence for recurring tasks.

        The completed original is kept in the pet's task list as a historical
        record. For daily and weekly tasks a fresh clone is created via
        ``dataclasses.replace`` (resetting ``completed`` and
        ``last_completed_date``) and appended to the pet so it reappears in the
        next scheduling cycle. Non-recurring frequencies ("monthly", "as needed",
        etc.) are marked done with no follow-up copy.

        Args:
            pet:  The Pet that owns the task. The new occurrence, if created,
                  is added directly to ``pet.tasks``.
            task: The Task instance to complete. Must belong to ``pet``.

        Returns:
            The newly created Task instance if the frequency is "daily" or
            "weekly", otherwise ``None``.
        """
        task.mark_complete()

        if task.frequency not in ("daily", "weekly"):
            return None  # "monthly", "as needed", etc. — no auto-recurrence

        next_occurrence = replace(task, completed=False, last_completed_date=None)
        pet.add_task(next_occurrence)
        return next_occurrence

    def fits_in_schedule(self) -> bool:
        """Return True if total daily task time fits within the owner's available hours."""
        return self.total_daily_minutes() <= self.owner.time_available_per_day * 60

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs sorted by scheduled_time in ascending order.

        Algorithm:
            Converts each "HH:MM" string to a plain integer by stripping the
            colon (e.g. "08:30" → 830). Because hours are always zero-padded,
            integer and lexicographic ordering are equivalent, so no ``datetime``
            import is required.

        Returns:
            A new list of ``(Pet, Task)`` tuples ordered earliest-to-latest by
            ``task.scheduled_time``. The original pet task lists are not mutated.
        """
        return sorted(
            self.get_all_tasks(),
            key=lambda pair: int(pair[1].scheduled_time.replace(":", ""))
        )

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs filtered by pet name and/or completion status.

        Filters are applied sequentially and are independently optional — pass
        neither to get all tasks, or combine both to narrow results further
        (e.g. all pending tasks for a specific pet).

        Args:
            pet_name:  Case-sensitive name of the pet to include. If ``None``,
                       tasks from all pets are considered.
            completed: ``True`` to return only completed tasks, ``False`` to
                       return only pending tasks, ``None`` to return tasks
                       regardless of completion status.

        Returns:
            A list of ``(Pet, Task)`` tuples that satisfy all supplied filters.
            Returns an empty list if no tasks match.
        """
        results = self.get_all_tasks()
        if pet_name is not None:
            results = [(p, t) for p, t in results if p.name == pet_name]
        if completed is not None:
            results = [(p, t) for p, t in results if t.completed == completed]
        return results

    def get_conflicts(self) -> list[str]:
        """Detect scheduling conflicts among all pending tasks and return warning messages.

        Algorithm:
            Each pending task's time window is modelled as an interval
            ``[start, start + duration)`` in minutes-since-midnight. Every
            unique pair of tasks is tested with the standard interval-overlap
            condition::

                start_a < end_b  AND  start_b < end_a

            Pairs that satisfy this condition are reported as conflicts.
            Completed tasks are excluded — only live, pending tasks can clash.

        Conflict severity:
            ``HARD`` — both tasks belong to the same pet (physically impossible
            for the owner to perform simultaneously).
            ``SOFT`` — tasks belong to different pets (may still be manageable,
            e.g. two pets on the same walk).

        Returns:
            A list of human-readable warning strings, one per conflicting pair.
            Each string includes the conflict type, task names, pet names, and
            the exact overlapping time windows. Returns an empty list when no
            conflicts are found.
        """
        def to_minutes(hhmm: str) -> int:
            h, m = hhmm.split(":")
            return int(h) * 60 + int(m)

        pending = self.get_pending_tasks()
        warnings: list[str] = []

        for i in range(len(pending)):
            for j in range(i + 1, len(pending)):
                pet_a, task_a = pending[i]
                pet_b, task_b = pending[j]

                start_a = to_minutes(task_a.scheduled_time)
                end_a   = start_a + task_a.duration_minutes
                start_b = to_minutes(task_b.scheduled_time)
                end_b   = start_b + task_b.duration_minutes

                if start_a < end_b and start_b < end_a:
                    kind = "HARD" if pet_a.name == pet_b.name else "SOFT"
                    warnings.append(
                        f"[{kind} CONFLICT] '{task_a.name}' ({pet_a.name}, "
                        f"{task_a.scheduled_time}–{end_a // 60:02d}:{end_a % 60:02d}) "
                        f"overlaps '{task_b.name}' ({pet_b.name}, "
                        f"{task_b.scheduled_time}–{end_b // 60:02d}:{end_b % 60:02d})"
                    )

        return warnings

    def display_schedule(self) -> None:
        """Print all pending tasks and daily time usage to the console."""
        print(f"\n=== Schedule for {self.owner.name} ({date.today()}) ===")
        for pet, task in self.get_pending_tasks():
            status = "[x]" if task.completed else "[ ]"
            print(f"  {status} [{pet.name}] {task.name} — {task.duration_minutes} min ({task.priority} priority, {task.frequency})")
        daily_mins = self.total_daily_minutes()
        available_mins = self.owner.time_available_per_day * 60
        print(f"\nDaily tasks: {daily_mins} min / {available_mins:.0f} min available")
