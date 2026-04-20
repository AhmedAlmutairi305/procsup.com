from __future__ import annotations

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


class RunStatus(str, Enum):
    queued = "queued"
    preparing = "preparing"
    running = "running"
    waiting_manual_action = "waiting_manual_action"
    waiting_email_verification = "waiting_email_verification"
    paused = "paused"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ManualActionType(str, Enum):
    login_submit = "login_submit"
    signup_submit = "signup_submit"
    email_verification_continue = "email_verification_continue"
    final_application_submit = "final_application_submit"


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(120), unique=True)
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
    runs = relationship("AutomationRun", back_populates="university", cascade="all, delete-orphan")


class ApplicantProfile(Base):
    __tablename__ = "applicant_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    applicant_id: Mapped[str] = mapped_column(String(100), index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(120))
    middle_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    chinese_name: Mapped[str | None] = mapped_column(String(120))
    gender: Mapped[str | None] = mapped_column(String(30))
    date_of_birth: Mapped[str | None] = mapped_column(String(40))
    nationality: Mapped[str | None] = mapped_column(String(80))
    passport_number: Mapped[str | None] = mapped_column(String(100))
    passport_expiry: Mapped[str | None] = mapped_column(String(40))
    marital_status: Mapped[str | None] = mapped_column(String(40))
    religion: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str | None] = mapped_column(String(255))
    email_password_reference: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(80))
    country: Mapped[str | None] = mapped_column(String(80))
    city: Mapped[str | None] = mapped_column(String(80))
    address_line_1: Mapped[str | None] = mapped_column(String(255))
    address_line_2: Mapped[str | None] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(40))
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(80))
    emergency_contact_relationship: Mapped[str | None] = mapped_column(String(80))
    high_school_name: Mapped[str | None] = mapped_column(String(255))
    previous_university: Mapped[str | None] = mapped_column(String(255))
    graduation_date: Mapped[str | None] = mapped_column(String(40))
    gpa: Mapped[str | None] = mapped_column(String(40))
    intended_degree_level: Mapped[str | None] = mapped_column(String(80))
    intended_major: Mapped[str | None] = mapped_column(String(120))
    intended_language: Mapped[str | None] = mapped_column(String(80))
    scholarship_type: Mapped[str | None] = mapped_column(String(120))
    supervisor_preference: Mapped[str | None] = mapped_column(String(120))
    study_plan_text: Mapped[str | None] = mapped_column(Text)
    personal_statement_text: Mapped[str | None] = mapped_column(Text)
    cv_text: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    # document mapping columns
    passport_file: Mapped[str | None] = mapped_column(String(600))
    transcript_file: Mapped[str | None] = mapped_column(String(600))
    graduation_certificate_file: Mapped[str | None] = mapped_column(String(600))
    cv_file: Mapped[str | None] = mapped_column(String(600))
    study_plan_file: Mapped[str | None] = mapped_column(String(600))
    personal_statement_file: Mapped[str | None] = mapped_column(String(600))
    recommendation_1_file: Mapped[str | None] = mapped_column(String(600))
    recommendation_2_file: Mapped[str | None] = mapped_column(String(600))
    language_certificate_file: Mapped[str | None] = mapped_column(String(600))
    photo_file: Mapped[str | None] = mapped_column(String(600))
    medical_form_file: Mapped[str | None] = mapped_column(String(600))
    bank_statement_file: Mapped[str | None] = mapped_column(String(600))
    police_clearance_file: Mapped[str | None] = mapped_column(String(600))
    portfolio_file: Mapped[str | None] = mapped_column(String(600))
    other_file_1: Mapped[str | None] = mapped_column(String(600))
    other_file_2: Mapped[str | None] = mapped_column(String(600))

    source_filename: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    runs = relationship("AutomationRun", back_populates="applicant")


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


class AutomationRun(Base):
    __tablename__ = "automation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), nullable=False)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicant_profiles.id"), nullable=False)
    application_record_id: Mapped[int | None] = mapped_column(ForeignKey("application_records.id"))
    portal_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[RunStatus] = mapped_column(SQLEnum(RunStatus), default=RunStatus.queued, index=True)
    current_step: Mapped[str | None] = mapped_column(String(255))
    last_completed_step: Mapped[str | None] = mapped_column(String(255))
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    last_successful_action: Mapped[str | None] = mapped_column(String(255))
    current_warning_error: Mapped[str | None] = mapped_column(Text)
    captcha_required: Mapped[bool] = mapped_column(Boolean, default=False)
    waiting_email_verification: Mapped[bool] = mapped_column(Boolean, default=False)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=True)
    headed: Mapped[bool] = mapped_column(Boolean, default=True)
    selected_files_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    university = relationship("University", back_populates="runs")
    applicant = relationship("ApplicantProfile", back_populates="runs")
    events = relationship("RunEvent", back_populates="run", cascade="all, delete-orphan")
    screenshots = relationship("RunScreenshot", back_populates="run", cascade="all, delete-orphan")
    manual_actions = relationship("ManualAction", back_populates="run", cascade="all, delete-orphan")


class RunEvent(Base):
    __tablename__ = "run_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("automation_runs.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    level: Mapped[str] = mapped_column(String(20), default="INFO")
    message: Mapped[str] = mapped_column(Text)
    event_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run = relationship("AutomationRun", back_populates="events")


class RunScreenshot(Base):
    __tablename__ = "run_screenshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("automation_runs.id"), index=True)
    step: Mapped[str] = mapped_column(String(255))
    screenshot_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run = relationship("AutomationRun", back_populates="screenshots")


class ManualAction(Base):
    __tablename__ = "manual_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("automation_runs.id"), index=True)
    action_type: Mapped[ManualActionType] = mapped_column(SQLEnum(ManualActionType), index=True)
    approved: Mapped[bool | None] = mapped_column(Boolean)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run = relationship("AutomationRun", back_populates="manual_actions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("application_records.id"))
    university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id"))
    run_id: Mapped[int | None] = mapped_column(ForeignKey("automation_runs.id"), index=True)
    level: Mapped[str] = mapped_column(String(20), default="INFO")
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    screenshot_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application = relationship("ApplicationRecord", back_populates="logs")
