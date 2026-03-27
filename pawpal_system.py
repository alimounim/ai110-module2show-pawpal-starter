from dataclasses import dataclass
from datetime import date


@dataclass
class Pet:
    name: str
    specie: str
    age: int
    weight: float
    health_notes: str = ""

    def get_careplan(self) -> dict:
        pass

    def update_info(self, **kwargs) -> None:
        pass


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False

    def edit(self, **kwargs) -> None:
        pass

    def mark_complete(self) -> None:
        pass


class Owner:
    def __init__(self, name: str, email: str, time_available_per_day: float):
        self.name = name
        self.email = email
        self.time_available_per_day = time_available_per_day
        self.pets: list[Pet] = []
        self.schedules: list["Schedule"] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_schedule(self) -> list["Schedule"]:
        pass


class Schedule:
    def __init__(self, date: date, owner: Owner, pet: Pet):
        self.date = date
        self.owner = owner
        self.pet = pet
        self.task_list: list[Task] = []
        self.total_duration: float = 0.0

    def generate(self) -> None:
        pass

    def display(self) -> None:
        pass

    def export_plan(self) -> None:
        pass
