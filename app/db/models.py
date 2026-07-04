from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


class SchoolClass(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_filled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    fee: Mapped["Fee | None"] = relationship(back_populates="school_class", uselist=False)

    @property
    def seats_available(self) -> int:
        return max(0, self.capacity - self.seats_filled)

    @property
    def is_full(self) -> bool:
        return self.seats_filled >= self.capacity


class Fee(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), unique=True, nullable=False)
    admission_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    tuition_fee_annual: Mapped[int] = mapped_column(Integer, nullable=False)
    transport_fee_annual: Mapped[int] = mapped_column(Integer, nullable=False)

    school_class: Mapped["SchoolClass"] = relationship(back_populates="fee")


class TransportRoute(Base):
    __tablename__ = "transport_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pickup_point: Mapped[str] = mapped_column(String(200), nullable=False)
    monthly_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, connect_args={"check_same_thread": False})


def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
