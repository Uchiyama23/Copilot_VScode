import os
from contextlib import contextmanager
from pathlib import Path

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    try:
        secret_environment = st.secrets.get("APP_ENV", "")
        secret_url = st.secrets.get("DATABASE_URL", "")
    except Exception:
        secret_environment = ""
        secret_url = ""

    environment = os.getenv("APP_ENV", secret_environment or "development").lower()
    configured_url = os.getenv("DATABASE_URL") or secret_url

    if environment == "production":
        if not configured_url:
            raise RuntimeError("Defina DATABASE_URL para conectar ao banco de producao.")
        if not configured_url.startswith("mysql+"):
            raise RuntimeError("Em producao, DATABASE_URL deve apontar para um banco MySQL.")
        return configured_url

    if configured_url:
        return configured_url

    data_directory = Path(__file__).resolve().parent.parent / "data"
    data_directory.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_directory / 'uvas.db'}"


DATABASE_URL = _database_url()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=DATABASE_URL.startswith("mysql+"),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()