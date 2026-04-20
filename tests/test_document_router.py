from pathlib import Path
from types import SimpleNamespace

from app.services.document_router import build_document_plan


class FakeQuery:
    def all(self):
        return []


class FakeDb:
    def query(self, _):
        return FakeQuery()


def test_document_router_missing_files(tmp_path: Path):
    applicant = SimpleNamespace(passport_file="missing.pdf")
    for name in [
        "transcript_file","graduation_certificate_file","cv_file","study_plan_file","personal_statement_file","recommendation_1_file","recommendation_2_file",
        "language_certificate_file","photo_file","medical_form_file","bank_statement_file","police_clearance_file","portfolio_file","other_file_1","other_file_2"
    ]:
        setattr(applicant, name, None)

    plan = build_document_plan(FakeDb(), applicant, {"upload_mappings": {}}, base_dir=str(tmp_path))
    assert plan["selected_files"]["passport_file"] is None
    assert any("passport_file" in w for w in plan["warnings"])
