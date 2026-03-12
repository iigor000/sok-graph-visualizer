import shlex
from .cli_command import CLICommand
from datetime import datetime, date


class CLIParser:
    """
    Parses CLI input strings into structured CLICommand objects.

    This parser interprets user commands entered as strings, supporting both
    single-word commands (like 'clear') and more complex commands with
    entities and properties (like 'create node --id=1 --prop Name=Alice').

    It also attempts to automatically convert property values to their
    appropriate Python types (int, float, date, datetime) for downstream use.
    """

    def parse(self, command_str: str) -> CLICommand:
        """
        Parse a CLI input string into a CLICommand object.

        Args:
            command_str (str): The raw input string from the user.

        Returns:
            CLICommand: A structured command object containing the command
                        name and parsed parameters.

        Raises:
            ValueError: If the input string is empty or has an invalid format.
        """
        tokens = shlex.split(command_str)

        if not tokens:
            raise ValueError("Empty command")
        if tokens[0] == "clear":
            return CLICommand("clear")
        if tokens[0] == "filter":
            return CLICommand("filter", {"expression": tokens[1]})
        if tokens[0] == "search":
            return CLICommand("search", {"expression": tokens[1]})

        if len(tokens) < 2:
            raise ValueError("Invalid command")

        action = tokens[0]
        entity = tokens[1]

        command_name = f"{action}_{entity}"

        params = {}
        properties = {}

        i = 2
        while i < len(tokens):
            token = tokens[i]

            if token.startswith("--id="):
                params["id"] = token.split("=", 1)[1]
            elif token.startswith("--source="):
                params["source"] = token.split("=", 1)[1]
            elif token.startswith("--target="):
                params["target"] = token.split("=", 1)[1]
            elif token == "--prop":
                key, value = tokens[i + 1].split("=", 1)
                properties[key] = self._normalize_value(value)
                i += 1

            i += 1

        if properties:
            params["properties"] = properties

        return CLICommand(command_name, params)
    
    def _normalize_value(self, value):
        """
        Attempt to convert a string value to int, float, datetime, or date.

        Conversion order:
            1. int
            2. float
            3. datetime.fromisoformat
            4. date.fromisoformat
            5. fallback: leave as string

        Args:
            value (str): The raw string value from the CLI.

        Returns:
            int, float, datetime, date, or str: The converted value in the
                                                 appropriate Python type.
        """
        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass

        try:
            return date.fromisoformat(value)
        except ValueError:
            pass

        return value