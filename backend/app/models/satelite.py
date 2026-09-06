from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Satellite(Base):
    __tablename__= "satellites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    norad_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    international_designator: Mapped[str | None] = mapped_column(String(32), nullable=True)
    orbit_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # One-to-many relationship: a satellite has many TLE records over time
    tles: Mapped[list["TLE"]] = relationship(
        "TLE", back_populates="satellite", cascade="all, delete-orphan"
    )

class TLE(Base):
    __tablename__ = "tles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    satellite_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("satellites.id"), nullable=False
    )
    line1: Mapped[str] = mapped_column(Text, nullable=False)
    line2: Mapped[str] = mapped_column(Text, nullable=False)
    epoch: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Orbital elements extracted from line2 for queryability
    inclination: Mapped[float] = mapped_column(Float, nullable=True)
    raan: Mapped[float] = mapped_column(Float, nullable=True)
    eccentricity: Mapped[float] = mapped_column(Float, nullable=True)
    arg_perigee: Mapped[float] = mapped_column(Float, nullable=True)
    mean_anomaly: Mapped[float] = mapped_column(Float, nullable=True)
    mean_motion: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Many-to-one relationship back to the parent Satellite
    satellite: Mapped["Satellite"] = relationship("Satellite", back_populates="tles")

    def __repr__(self) -> str:
        return f"<TLE(satellite_id={self.satellite_id}, epoch={self.epoch})>"
