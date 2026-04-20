from __future__ import annotations

from app.models.models import ApplicantProfile
from app.services.normalization import normalize_country, normalize_date, normalize_gender, normalize_nationality, normalize_phone


def canonical_profile_dict(applicant: ApplicantProfile) -> dict:
    payload = {c.name: getattr(applicant, c.name) for c in applicant.__table__.columns}
    payload["gender"] = normalize_gender(payload.get("gender"))
    payload["date_of_birth"] = normalize_date(payload.get("date_of_birth"))
    payload["passport_expiry"] = normalize_date(payload.get("passport_expiry"))
    payload["graduation_date"] = normalize_date(payload.get("graduation_date"))
    payload["phone"] = normalize_phone(payload.get("phone"))
    payload["emergency_contact_phone"] = normalize_phone(payload.get("emergency_contact_phone"))
    payload["nationality"] = normalize_nationality(payload.get("nationality"))
    payload["country"] = normalize_country(payload.get("country"))
    return payload


def map_fields(applicant: ApplicantProfile, recipe: dict) -> list[dict]:
    src = canonical_profile_dict(applicant)
    mapping = recipe.get("field_mappings", {})
    output: list[dict] = []
    for canonical, selector_config in mapping.items():
        value = src.get(canonical)
        transformed = value
        transform = selector_config.get("transform") if isinstance(selector_config, dict) else None
        if transform == "date_dd_mm_yyyy" and value:
            transformed = normalize_date(str(value), "%d/%m/%Y")
        output.append(
            {
                "canonical_field": canonical,
                "selector": selector_config.get("selector") if isinstance(selector_config, dict) else str(selector_config),
                "field_type": selector_config.get("type", "text") if isinstance(selector_config, dict) else "text",
                "value": transformed,
                "confidence": 1.0 if value else 0.0,
            }
        )
    return output
