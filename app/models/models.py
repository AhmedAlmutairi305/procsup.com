from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UniversityStatus(str, Enum):
    planned = "planned"
    preparing = "preparing"
    ready_for_review = "ready_for_review"
    submitted = "submitted"
    follow_up = "follow_up"


class AutomationStatus(str, Enum):
    pending = "pending"
    running = "running"
    paused_for_captcha = "paused_for_captcha"
    paused_for_review = "paused_for_review"
    failed = "failed"
    completed_prepared = "completed_prepared"
    completed_submitted = "completed_submitted"


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    portal_url: Mapped[str] = mapped_column(String(500), nullable=False)
    deadline: Mapped[str | None] = mapped_column(String(100))
    degree_level: Mapped[str | None] = mapped_column(String(50))
    language_of_instruction: Mapped[str | None] = mapped_column(String(50))
    scholarship_available: Mapped[bool] = mapped_column(Boolean, default=False)
    application_fee: Mapped[float | None] = mapped_column(Float)
    recommendation_letter_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[UniversityStatus] = mapped_column(SQLEnum(UniversityStatus), default=UniversityStatus.planned)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirements = relationship("Requirement", back_populates="university", cascade="all, delete-orphan")
    applications = relationship("ApplicationRecord", back_populates="university", cascade="all, delete-orphan")


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), nullable=False, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_json: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_deadline: Mapped[str | None] = mapped_column(String(100))
    extracted_language_requirement: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    university = relationship("University", back_populates="requirements")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(600), nullable=False, unique=True)
    tag: Mapped[str] = mapped_column(String(100), index=True)
    extra_tags: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentMatch(Base):
    __tablename__ = "document_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), nullable=False)
    requirement_key: Mapped[str] = mapped_column(String(120), nullable=False)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    mismatch_warning: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApplicationRecord(Base):
    __tablename__ = "application_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), nullable=False)
    portal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username_hint: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[AutomationStatus] = mapped_column(SQLEnum(AutomationStatus), default=AutomationStatus.pending)
    submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    pending_items: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    university = relationship("University", back_populates="applications")
    logs = relationship("AuditLog", back_populates="application", cascade="all, delete-orphan")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("application_records.id"))
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id"))
    level: Mapped[str] = mapped_column(String(20), default="INFO")
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    screenshot_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application = relationship("ApplicationRecord", back_populates="logs")
