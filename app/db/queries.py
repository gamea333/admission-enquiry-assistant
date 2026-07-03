from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import AdmissionDeadline, FAQ, Program


def get_all_programs(db: Session) -> list[Program]:
    return db.query(Program).order_by(Program.name).all()


def get_program_by_name(db: Session, name: str) -> Program | None:
    return db.query(Program).filter(Program.name.ilike(f"%{name}%")).first()


def get_upcoming_deadlines(db: Session, after: datetime | None = None) -> list[AdmissionDeadline]:
    cutoff = after or datetime.utcnow()
    return (
        db.query(AdmissionDeadline)
        .filter(AdmissionDeadline.deadline_date >= cutoff)
        .order_by(AdmissionDeadline.deadline_date)
        .all()
    )


def search_faqs(db: Session, keyword: str, limit: int = 5) -> list[FAQ]:
    pattern = f"%{keyword}%"
    return (
        db.query(FAQ)
        .filter(FAQ.question.ilike(pattern) | FAQ.answer.ilike(pattern))
        .limit(limit)
        .all()
    )


def get_faqs_by_category(db: Session, category: str) -> list[FAQ]:
    return db.query(FAQ).filter(FAQ.category.ilike(category)).all()
