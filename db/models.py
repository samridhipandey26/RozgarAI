"""
db/models.py — SQLAlchemy ORM Models
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, Float, ForeignKey, Integer,
    String, Text, create_engine, func,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship

import os

DB_PATH = os.getenv("DB_PATH", "data/rozgar.db")


class Base(DeclarativeBase):
    pass


class Worker(Base):
    __tablename__ = "workers"

    worker_id             = Column(String, primary_key=True)
    name                  = Column(String, nullable=False)
    phone                 = Column(String, unique=True, nullable=False)
    city                  = Column(String, nullable=False)
    pin_code              = Column(String, nullable=False)
    skills                = Column(Text, nullable=False)          # JSON array
    experience_years      = Column(Integer, default=0)
    preferred_wage_per_day= Column(Integer, default=0)
    trust_score           = Column(Float, default=3.0)
    total_jobs_done       = Column(Integer, default=0)
    created_at            = Column(String, default=lambda: datetime.utcnow().isoformat())

    applications = relationship("Application", back_populates="worker")

    @property
    def skills_list(self) -> List[str]:
        return json.loads(self.skills)

    @skills_list.setter
    def skills_list(self, val: List[str]):
        self.skills = json.dumps(val)


class Contractor(Base):
    __tablename__ = "contractors"

    contractor_id = Column(String, primary_key=True)
    name          = Column(String, nullable=False)
    phone         = Column(String, unique=True, nullable=False)
    company_name  = Column(String)
    city          = Column(String, nullable=False)
    verified      = Column(Boolean, default=False)
    created_at    = Column(String, default=lambda: datetime.utcnow().isoformat())

    jobs = relationship("Job", back_populates="contractor")


class Job(Base):
    __tablename__ = "jobs"

    job_id          = Column(String, primary_key=True)
    contractor_id   = Column(String, ForeignKey("contractors.contractor_id"), nullable=False)
    title           = Column(String, nullable=False)
    title_hindi     = Column(String, nullable=False)
    location        = Column(String, nullable=False)
    pin_code        = Column(String, nullable=False)
    wage_per_day    = Column(Integer, nullable=False)
    skills_required = Column(Text, nullable=False)   # JSON array
    start_date      = Column(String, nullable=False)
    openings        = Column(Integer, default=1)
    filled          = Column(Integer, default=0)
    status          = Column(String, default="open")
    created_at      = Column(String, default=lambda: datetime.utcnow().isoformat())

    contractor   = relationship("Contractor", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

    @property
    def skills_list(self) -> List[str]:
        return json.loads(self.skills_required)

    @skills_list.setter
    def skills_list(self, val: List[str]):
        self.skills_required = json.dumps(val)


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(String, primary_key=True)
    worker_id      = Column(String, ForeignKey("workers.worker_id"), nullable=False)
    job_id         = Column(String, ForeignKey("jobs.job_id"), nullable=False)
    status         = Column(String, default="pending")
    otp            = Column(String)
    otp_verified   = Column(Boolean, default=False)
    applied_at     = Column(String, default=lambda: datetime.utcnow().isoformat())
    completed_at   = Column(String)

    worker = relationship("Worker", back_populates="applications")
    job    = relationship("Job",    back_populates="applications")


class AppSession(Base):
    __tablename__ = "sessions"

    session_id      = Column(String, primary_key=True)
    worker_phone    = Column(String)
    stage_reached   = Column(String)
    transcript      = Column(Text)
    matched_job_ids = Column(Text)   # JSON array
    outcome         = Column(String)
    created_at      = Column(String, default=lambda: datetime.utcnow().isoformat())


# ── Engine factory ─────────────────────────────────────────────────────────────

def get_engine(db_path: str = DB_PATH):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session(db_path: str = DB_PATH) -> Session:
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return Session(engine)
