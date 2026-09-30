"""The one exception type of the CLI: a problem with the request or the environment, with a message that says how to fix it."""


class PtError(Exception):
    """A problem with the request (unknown field, ambiguous resource, missing data, ...). The message says how to fix it."""
