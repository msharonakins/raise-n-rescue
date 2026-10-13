from backend.app.security.email import normalize_email


def test_normalize_email_strips_surrounding_whitespace():
    assert normalize_email("  person@example.com  ") == "person@example.com"


def test_normalize_email_lowercases_address():
    assert normalize_email("Person@Example.COM") == "person@example.com"


def test_normalize_email_strips_whitespace_and_lowercases_address():
    assert normalize_email("  Person@Example.COM  ") == "person@example.com"


def test_normalize_email_preserves_internal_characters():
    assert normalize_email("first.last+rescue@example.com") == (
        "first.last+rescue@example.com"
    )
