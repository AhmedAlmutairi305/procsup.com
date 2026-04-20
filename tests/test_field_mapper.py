from types import SimpleNamespace

from app.services.field_mapper import map_fields


def test_map_fields_basic():
    applicant = SimpleNamespace(
        __table__=SimpleNamespace(columns=[SimpleNamespace(name="full_name"), SimpleNamespace(name="gender"), SimpleNamespace(name="date_of_birth")]),
        full_name="Anna Zhang",
        gender="female",
        date_of_birth="2003-05-20",
    )
    recipe = {
        "field_mappings": {
            "full_name": {"selector": "#fullName", "type": "text"},
            "gender": {"selector": "#gender", "type": "dropdown"},
            "date_of_birth": {"selector": "#dob", "type": "date", "transform": "date_dd_mm_yyyy"},
        }
    }
    mapped = map_fields(applicant, recipe)
    assert len(mapped) == 3
    assert mapped[0]["selector"] == "#fullName"
    assert mapped[2]["value"] == "20/05/2003"
