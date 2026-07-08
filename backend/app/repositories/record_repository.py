from sqlalchemy.orm import Session


class RecordRepository:
    """Repository scaffold for future record persistence queries."""

    def __init__(self, db: Session) -> None:
        self.db = db
