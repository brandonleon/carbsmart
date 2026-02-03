from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Pan(Base):
    __tablename__ = "pans"
    __table_args__ = (UniqueConstraint("name", "capacity_label", name="uq_pans_name_capacity"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    weight_grams: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
        server_default="",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
