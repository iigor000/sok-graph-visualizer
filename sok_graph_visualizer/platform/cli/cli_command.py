class CLICommand:
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or {}

    def __repr__(self):
        return f"CLICommand(name={self.name}, params={self.params})"