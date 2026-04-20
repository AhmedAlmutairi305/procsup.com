import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.models import University


def _slugify(name: str) -> str:
    return "-".join(name.lower().strip().split())


def import_universities_csv(db: Session, csv_path: str) -> int:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    created = 0
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uni = University(
                name=row["name"],
                slug=row.get("slug") or _slugify(row["name"]),
                portal_url=row["portal_url"],
                deadline=row.get("deadline"),
                degree_level=row.get("degree_level"),
                language_of_instruction=row.get("language_of_instruction"),
                scholarship_available=str(row.get("scholarship_available", "")).lower() == "true",
                notes=row.get("notes"),
            )
            db.add(uni)
            created += 1
    db.commit()
    return created
