from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_years: Mapped[float] = mapped_column(Float, nullable=False)
    tuition_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    eligibility: Mapped[str] = mapped_column(Text, nullable=False)
    intake_month: Mapped[str] = mapped_column(String(50), nullable=False)


class AdmissionDeadline(Base):
    __tablename__ = "admission_deadlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    program_name: Mapped[str] = mapped_column(String(200), nullable=False)
    round: Mapped[str] = mapped_column(String(50), nullable=False)
    deadline_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, connect_args={"check_same_thread": False})


def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
