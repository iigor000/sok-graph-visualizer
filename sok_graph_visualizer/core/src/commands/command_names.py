from enum import Enum

class CommandNames(str, Enum):
    #Graph search and filtering
    SEARCH = "search"
    FILTER = "filter"
    CLEAR_SEARCH = "clear-search"
    REMOVE_FILTER = "remove-filter"

    #Other commands...