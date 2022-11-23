from typing import Protocol
from app.core.schemas.system import Onu


class Task(Protocol):
    description: str
    onu: Onu

    def execute(self):
        ...
