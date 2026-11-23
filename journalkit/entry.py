from datetime import datetime, timezone


class JournalEntry:
    """One timestamped journal note."""

    def __init__(self, text, mood="neutral", created_at=None):
        text = text.strip()
        if not text:
            raise ValueError("Journal entry text cannot be empty")
        self.text = text
        self.mood = mood.strip() or "neutral"
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def as_dict(self):
        return {
            "text": self.text,
            "mood": self.mood,
            "created_at": self.created_at,
        }


def create_entry(text, mood="neutral"):
    """Create a new timestamped journal entry."""
    return JournalEntry(text=text, mood=mood)
