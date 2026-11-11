"""Tight controls for the educational sandbox."""
from pathlib import Path
from .fixture import BUGGY, FIXED

class SecurityViolation(ValueError):
    pass

def bounded_patch(source: str) -> str:
    if source != BUGGY:
        raise SecurityViolation("Source does not match the reviewed demo fixture")
    return FIXED

