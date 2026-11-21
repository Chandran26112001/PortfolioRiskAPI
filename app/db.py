"""Database engine, sessions and shared helpers."""

from collections.abc import Iterator

import oracledb
from sqlalchemy import Select, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.errors import ConflictError
from app.schemas.pagination import PageParams

# One connection pool per process. pool_pre_ping checks a pooled connection is still
# alive before handing it out, so a database restart doesn't surface as request errors.
engine = create_engine(
    get_settings().database_url, pool_pre_ping=True, echo=get_settings().sql_echo
)

# expire_on_commit=False keeps loaded values readable after the commit.
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """One session and transaction per request: commit on success, roll back on any error."""
    with SessionLocal.begin() as session:
        yield session


def fetch_page[T](session: Session, query: Select[T], page: PageParams) -> tuple[list[T], int]:
    """Run one page of an ordered query, plus a COUNT of all matching rows.

    On Oracle, limit/offset become OFFSET n ROWS FETCH NEXT m ROWS ONLY.
    """
    total = session.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    items = list(session.scalars(query.limit(page.limit).offset(page.offset)))
    return items, total or 0


def flush_or_conflict(session: Session, message: str) -> None:
    """Send pending inserts now, turning a unique-key violation into a ConflictError."""
    try:
        session.flush()
    except IntegrityError as exc:
        if _is_unique_violation(exc):
            raise ConflictError(message) from exc
        raise


def _is_unique_violation(exc: IntegrityError) -> bool:
    """ORA-00001: unique constraint violated."""
    error = exc.orig
    return isinstance(error, oracledb.IntegrityError) and error.args[0].code == 1
