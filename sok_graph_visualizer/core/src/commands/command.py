from abc import ABC, abstractmethod
from typing import Tuple

class Command(ABC):
    """
    Abstract base class for all commands in the system.
    This class represents the base interface in the Command design pattern.
    Concrete command classes must inherit from this class and implement
    the `execute()` method.
    Each command encapsulates a specific operation that can be executed
    within the application (e.g. filter graph, search nodes, create node,
    delete edge, etc.).

    The command should contain all necessary data and dependencies required
    to perform its operation."""

    @abstractmethod
    def execute(self) -> Tuple[bool, str]:
        """
        Execute the command.
        This method must be implemented by all concrete command classes.
        Returns:
            Tuple[bool, str]:
                A tuple containing:
                - success flag (True if the command executed successfully)
                - message describing the outcome of the command
        """
        pass