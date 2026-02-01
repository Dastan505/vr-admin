from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SessionStatus


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)

    start_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=False)
    end_at: Mapped[DateTime] = mapped_column(DateTime(), nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[SessionStatus] = mapped_column(
        SqlEnum(SessionStatus, name="session_status"), default=SessionStatus.planned, nullable=False
    )

    players: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    canceled_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    canceled_at: Mapped[DateTime | None] = mapped_column(DateTime(), nullable=True)
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(), nullable=True)

    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    location = relationship("Location", back_populates="sessions")
    resource = relationship("Resource", back_populates="sessions")
    game = relationship("Game", back_populates="sessions")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_sessions")
    updated_by = relationship("User", foreign_keys=[updated_by_id], back_populates="updated_sessions")
