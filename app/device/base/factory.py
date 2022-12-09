"""Factory for creating a game character."""
from typing import Any, Callable
from app.device.base.device_base import OltDeviceBase

device_creation_funcs: dict[str, Callable[..., OltDeviceBase]] = {}


def register(device_type: str, creator_fn: Callable[..., OltDeviceBase]) -> None:
    """Register a new game character type."""
    device_creation_funcs[device_type] = creator_fn


def unregister(device_type: str) -> None:
    """Unregister a game character type."""
    device_creation_funcs.pop(device_type, None)


def create(arguments: dict[str, Any]) -> OltDeviceBase:
    """Create a game character of a specific type, given JSON data."""
    args_copy = arguments.copy()
    device_type = args_copy.pop("type")
    try:
        creator_func = device_creation_funcs[device_type]
    except KeyError:
        raise ValueError(f"unknown device type {device_type!r}") from None
    return creator_func(**args_copy)
