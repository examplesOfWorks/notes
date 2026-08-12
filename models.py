from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(100)
    )

    text: Mapped[str] = mapped_column(
        String(5000)
    )

    image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )