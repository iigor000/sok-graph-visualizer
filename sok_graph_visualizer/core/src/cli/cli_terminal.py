from sok_graph_visualizer.core.src.app import App

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge

class CLITerminal:
    """
    Provides a command-line interface for interacting with the Sok Graph Visualizer.

    The CLITerminal reads commands from the user, parses them using a CLIParser,
    executes them through the application's CommandProcessor.

    Attributes:
        app (App): The main application instance, containing workspaces and command processor.
        parser (CLIParser): The parser used to convert raw CLI strings into CLICommand objects.
    """
    def __init__(self, app, parser):
        """
        Initialize the CLITerminal.

        Args:
            app (App): The application instance.
            parser (CLIParser): The CLI parser instance.
        """
        self.app = app
        self.parser = parser

    def run(self):
        """
        Run the CLI terminal loop, continuously reading user input.

        Workflow:
            1. Waits for input from the user (e.g., 'create node --id=1 --prop Name=Alice').
            2. If input is "exit", terminates the loop.
            3. Parses the input string using the CLIParser.
            4. Executes the parsed command using the application's CommandProcessor.
            5. Prints the result of the command execution (success or error message).

        Exceptions:
            Catches any exceptions during parsing or execution and prints an error message.
        """
        while True:
            command = input("> ")

            if command == "exit":
                break

            try:
                parsed = self.parser.parse(command)

                success, message = self.app.command_processor.execute_command(
                    parsed.name,
                    parsed.params
                )

                print(message)

            except Exception as e:
                print(f"Error: {e}")