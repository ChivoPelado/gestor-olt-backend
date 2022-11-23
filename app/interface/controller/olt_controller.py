"""
Invoker Class
"""
import time
from dataclasses import dataclass
from datetime import datetime
from app.interface.task import Task

@dataclass
class OltController:
    _commands = {}
    _history = []

    def get(self, task: Task) -> None:
        self._history.append((time.time(), task.description, str(task.onu), str(task.onu.olt)))
        return task.execute()

    def register(self, task: Task) -> None:
        self._commands[task] = task

    def get_command_history(self):
        for row in self._history:
            print(
                f"{datetime.fromtimestamp(row[0]).strftime('%d-%B-%Y %H:%M:%S')}"
                f" : {row[1]}"
                f" : {row[2]}"
                f" : {row[3]}"
            )