from sqlalchemy.orm import Session

from app.models.record import Record


class RecordRepository:
    """Persistence gateway for valid Record rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_many(self, records: list[dict]) -> int:
        if not records:
            return 0
        self.db.bulk_insert_mappings(Record, records)
        self.db.commit()
        return len(records)

    def list_paginated(self, *, limit: int, offset: int) -> list[Record]:
        return (
            self.db.query(Record)
            .order_by(Record.created_at.desc(), Record.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count(self) -> int:
        return self.db.query(Record).count()
