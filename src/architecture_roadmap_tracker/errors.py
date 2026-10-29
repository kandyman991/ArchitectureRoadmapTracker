"""Shared domain command errors; no UI, GitHub or storage dependencies."""


class TreeError(ValueError):
    """A command was rejected without changing canonical state."""


class NotFound(TreeError):
    """A project-scoped entity was not found."""


class InvalidMove(TreeError):
    """Unsafe reparent, cycle or archived-node operation."""
