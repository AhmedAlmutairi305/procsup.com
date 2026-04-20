from __future__ import annotations

from datetime import datetime
import re


COUNTRY_MAP = {
    "china": "China",
    "people's republic of china": "China",
    "usa": "United States",
    "us": "United States",
    "united states of america": "United States",
}

NATIONALITY_MAP = {
    "chinese": "Chinese",
    "american": "American",
}

GENDER_MAP = {
    "male": "M",
    "m": "M",
    "female": "F",
    "f": "F",
    "other": "O",
}


def normalize_gender(value: str | None) -> str | None:
    if not value:
        return None
    return GENDER_MAP.get(value.strip().lower(), value.strip())


def normalize_country(value: str | None) -> str | None:
    if not value:
        return None
    return COUNTRY_MAP.get(value.strip().lower(), value.strip())


def normalize_nationality(value: str | None) -> str | None:
    if not value:
        return None
    return NATIONALITY_MAP.get(value.strip().lower(), value.strip())


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"[^0-9+]", "", value)
    return digits


def normalize_date(value: str | None, out_format: str = "%Y-%m-%d") -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    fmts = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
    for fmt in fmts:
        try:
            return datetime.strptime(cleaned, fmt).strftime(out_format)
        except ValueError:
            continue
    return cleaned
