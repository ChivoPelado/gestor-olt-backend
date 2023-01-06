"""Plugin loader simple"""
import importlib


class ModuleInterface:
    """Representa un Plugin Interface."""

    @staticmethod
    def register() -> None:
        """Registra los items necesarios en la fabrica (factory) de dispositivos."""


def import_module(name: str) -> ModuleInterface:
    """Imports un modulo bajo un nombre dado."""
    return importlib.import_module(name)  # type: ignore


def load_plugins(plugins: list[str]) -> None:
    """Carga el plugin en base a la lista de plugins."""
    for plugin_file in plugins:
        plugin = import_module(plugin_file)
        plugin.register()
