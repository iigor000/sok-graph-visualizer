from enum import Enum

class CommandNames(str, Enum):
    #Graph search and filtering
    SEARCH = "search"
    FILTER = "filter"
    CLEAR_SEARCH = "clear-search"
    REMOVE_FILTER = "remove-filter"

    # Node commands
    CREATE_NODE = "create_node"
    EDIT_NODE = "edit_node"
    DELETE_NODE = "delete_node"

    # Edge commands
    CREATE_EDGE = "create_edge"
    EDIT_EDGE = "edit_edge"
    DELETE_EDGE = "delete_edge"

    # Graph commands
    CLEAR_GRAPH = "clear"

    #Other commands...