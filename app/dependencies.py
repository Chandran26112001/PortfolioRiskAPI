"""Dependencies that FastAPI injects into route functions."""

from typing import Annotated

from fastapi import Depends

from app.store import InMemoryStore

_store = InMemoryStore()


def get_store() -> InMemoryStore:
    """Provide the single, process-wide store. Tests will override this dependency."""
    return _store


StoreDep = Annotated[InMemoryStore, Depends(get_store)]
