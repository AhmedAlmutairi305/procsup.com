from app.services.excel_importer import parse_applicant_file


def test_parse_applicant_csv():
    rows = parse_applicant_file("examples/applicant_template.csv")
    assert rows
    assert rows[0]["applicant_id"] == "A001"
    assert rows[0]["full_name"] == "Anna Zhang"
