from typing import Protocol
from app.interface.utils import Payload


class Task(Protocol):
    description: str
    payload: Payload

    def execute(self):
        ...
