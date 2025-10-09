from itertools import cycle
from typing import Iterator

# Curated modern desktop Chrome UAs (Windows/macOS)
_UAS = [
    # Windows Chrome variants only (remove Safari to avoid UA/UA-CH mismatches)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

_cycle: Iterator[str] = cycle(_UAS)

def get_next_user_agent() -> str:
    """Return the next user agent from the rotation pool."""
    return next(_cycle)

