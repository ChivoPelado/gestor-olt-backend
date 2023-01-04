from abc import ABC, abstractmethod
from app.device.base.device_base import OltDeviceBase


class ICommand(ABC):

    @property
    @abstractmethod
    def loggable(self) -> bool:
        ...

    @abstractmethod
    def execute(olt_vendor: OltDeviceBase) -> list[dict[str:any]]:
        ...

    @abstractmethod
    def description() -> str:
        ...

