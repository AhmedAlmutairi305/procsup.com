from datetime import datetime

from pydantic import BaseModel, Field

from app.models.models import AutomationStatus, UniversityStatus


class UniversityBase(BaseModel):
    name: str
    portal_url: str
    deadline: str | None = None
    degree_level: str | None = None
    language_of_instruction: str | None = None
    scholarship_available: bool = False
    application_fee: float | None = None
    recommendation_letter_count: int | None = None
    status: UniversityStatus = UniversityStatus.planned
    notes: str | None = None


class UniversityCreate(UniversityBase):
    pass


class UniversityRead(UniversityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RequirementParseRequest(BaseModel):
    university_id: int
    source_text: str = Field(min_length=20)


class RequirementRead(BaseModel):
    id: int
    university_id: int
    structured_json: str
    extracted_deadline: str | None
    extracted_language_requirement: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentRead(BaseModel):
    id: int
    filename: str
    file_path: str
    tag: str
    extra_tags: str | None

    model_config = {"from_attributes": True}


class MatchPreview(BaseModel):
    requirement_key: str
    matched_file: str | None
    confidence: float
    warning: str | None


class AutomationRequest(BaseModel):
    university_id: int
    application_id: int | None = None
    username: str | None = None
    dry_run: bool = True


class FinalSubmissionApproval(BaseModel):
    application_id: int
    approved: bool


class ApplicationRecordRead(BaseModel):
    id: int
    university_id: int
    portal_name: str
    username_hint: str | None
    status: AutomationStatus
    submitted: bool
    submitted_at: datetime | None
    pending_items: str | None

    model_config = {"from_attributes": True}
