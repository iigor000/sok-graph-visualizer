class CLICommand:
    """
    Represents a command entered in the CLI.

    This class encapsulates the command name and its associated parameters.
    It is used by the CLI parser to standardize the commands before they are
    executed by the application's command processor.

    Attributes:
        name (str): The name of the command, e.g., 'create_node', 'filter', 'search'.
        params (dict): Optional dictionary containing parameters for the command.
                       Defaults to an empty dictionary if not provided.
    """

    def __init__(self, name, params=None):
        """
        Initialize a new CLICommand instance.

        Args:
            name (str): The name of the CLI command.
            params (dict, optional): Parameters associated with the command.
                                     Defaults to None, which will be converted to an empty dict.
        """
        self.name = name
        self.params = params or {}

    def __repr__(self):
        """
        Return a string representation of the CLICommand.
        
        Returns:
            str: A string in the format 'CLICommand(name=<name>, params=<params>)'.
        """
        return f"CLICommand(name={self.name}, params={self.params})"