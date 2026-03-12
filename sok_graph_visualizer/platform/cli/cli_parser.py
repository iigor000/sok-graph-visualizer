import shlex
from .cli_command import CLICommand


class CLIParser:

    def parse(self, command_str: str) -> CLICommand:
        tokens = shlex.split(command_str)

        if not tokens:
            raise ValueError("Empty command")

        # clear
        if tokens[0] == "clear":
            return CLICommand("clear")

        # filter
        if tokens[0] == "filter":
            return CLICommand("filter", {"expression": tokens[1]})

        # search
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

            # --id=1
            if token.startswith("--id="):
                params["id"] = token.split("=", 1)[1]

            # --source=1
            elif token.startswith("--source="):
                params["source"] = token.split("=", 1)[1]

            # --target=2
            elif token.startswith("--target="):
                params["target"] = token.split("=", 1)[1]

            # --prop Name=Alice
            elif token == "--prop":
                key, value = tokens[i + 1].split("=", 1)
                properties[key] = value
                i += 1

            i += 1

        if properties:
            params["properties"] = properties

        return CLICommand(command_name, params)