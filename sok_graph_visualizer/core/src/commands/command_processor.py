from abc import ABC
from typing import Any, Callable, Dict, Tuple
from sok_graph_visualizer.core.src.commands.command import Command

class CommandProcessor:
    """
    Class responsible for registering and executing application commands.
    This class implements the *Invoker* role in the Command design pattern.
    It maintains a registry of command factories that are used to create
    concrete command instances at runtime.

    Instead of storing command objects directly, the processor stores
    factory functions. Each factory receives the command arguments and
    returns a new instance of a concrete Command.

    Attributes:
        _commands (Dict[str, Callable[[Dict[str, Any]], Command]]):
            A registry mapping command names to factory functions that
            produce concrete Command instances.
    
    """

    def __init__(self):
        """
        Initialize the command processor with an empty command registry.
        """
        self._commands: Dict[str,Callable[[Dict[str, Any]], Command]] = {}

    def register_command(self, command_name: str, factory: Callable[..., Command]) -> None:
        """
        Registers a new command factory.
        The factory is responsible for creating a concrete Command instance.
        It typically receives command arguments and injects required
        dependencies into the command constructor.

        Args:
            command_name (str):
                Unique identifier of the command (e.g. "filter", "search").

            factory (Callable[..., Command]):
                A callable that creates and returns a Command instance.

        """
        self._commands[command_name] = factory

    def execute_command(self, command_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Executes a command by its registered name with needed arguments.
        Args:
            command_name (str):
                Name of the command to execute.

            args (Dict[str, Any]):
                Dictionary of arguments required by the command.

        Returns:
            Tuple[bool, str]:
                A tuple containing:
                - success flag (True if execution succeeded)
                - message describing the result of the command.
        """
        if command_name not in self._commands:
            return False, f'Unknown command: {command_name}'

        command = self._commands[command_name](args)
        return command.execute()

