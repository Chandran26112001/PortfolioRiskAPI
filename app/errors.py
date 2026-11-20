"""Domain errors. They say what went wrong, not which HTTP status to send."""


class NotFoundError(Exception):
    """A requested record does not exist."""


class ConflictError(Exception):
    """A record with the same key already exists."""
