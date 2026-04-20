import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import SessionLocal
from app.db.init_db import init_db
from app.models.models import Document, University


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(University).count() == 0:
            db.add_all(
                [
                    University(
                        name="Tsinghua University",
                        slug="tsinghua-university",
                        portal_url="https://gradadmission.tsinghua.edu.cn",
                        degree_level="Masters",
                        language_of_instruction="English",
                        scholarship_available=True,
                        deadline="2026-12-15",
                        notes="Priority target.",
                    ),
                    University(
                        name="Peking University",
                        slug="peking-university",
                        portal_url="https://admission.pku.edu.cn",
                        degree_level="Masters",
                        language_of_instruction="Chinese",
                        scholarship_available=True,
                        deadline="2026-11-30",
                    ),
                ]
            )
        if db.query(Document).count() == 0:
            db.add_all(
                [
                    Document(filename="passport_anna.pdf", file_path="examples/document_library/passport_anna.pdf", tag="passport"),
                    Document(filename="transcript_anna.pdf", file_path="examples/document_library/transcript_anna.pdf", tag="transcript"),
                    Document(filename="cv_anna.pdf", file_path="examples/document_library/cv_anna.pdf", tag="cv"),
                ]
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
