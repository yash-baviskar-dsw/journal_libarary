"""A tiny journaling library."""

from .entry import JournalEntry, create_entry


class Journal:
    """Convenience API for creating journal entries."""

    create_entry = staticmethod(create_entry)


__all__ = ["Journal", "JournalEntry", "create_entry"]
