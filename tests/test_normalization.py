from app.services.normalization import normalize_country, normalize_date, normalize_gender, normalize_phone


def test_normalizations():
    assert normalize_gender("male") == "M"
    assert normalize_country("usa") == "United States"
    assert normalize_date("2024/01/31") == "2024-01-31"
    assert normalize_phone("+86 138-0000-1111") == "+8613800001111"
