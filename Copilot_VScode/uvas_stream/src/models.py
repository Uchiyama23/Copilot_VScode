from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class GrapeVariety(Base):
    __tablename__ = "grape_varieties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    color: Mapped[str] = mapped_column(String(40))
    origin: Mapped[str] = mapped_column(String(100))
    sweetness: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text, default="")
    harvests: Mapped[list["HarvestLot"]] = relationship(back_populates="variety")


class Producer(Base):
    __tablename__ = "producers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    municipality: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(80), default="Brasil")
    email: Mapped[str] = mapped_column(String(160), default="")
    phone: Mapped[str] = mapped_column(String(40), default="")
    sustainable: Mapped[bool] = mapped_column(Boolean, default=False)
    harvests: Mapped[list["HarvestLot"]] = relationship(back_populates="producer")


class HarvestLot(Base):
    __tablename__ = "harvest_lots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    variety_id: Mapped[int] = mapped_column(ForeignKey("grape_varieties.id"))
    producer_id: Mapped[int] = mapped_column(ForeignKey("producers.id"))
    harvest_date: Mapped[date] = mapped_column(Date)
    quantity_kg: Mapped[float] = mapped_column(Float)
    price_per_kg: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(Text, default="")
    variety: Mapped[GrapeVariety] = relationship(back_populates="harvests")
    producer: Mapped[Producer] = relationship(back_populates="harvests")