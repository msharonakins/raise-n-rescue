from backend.app.security.password import hash_password, verify_password


def test_hash_password_returns_a_hash_that_verifies():
    password = "correct horse battery staple"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_verify_password_rejects_wrong_password():
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("wrong password", password_hash) is False


def test_hash_password_produces_different_hashes_for_same_password():
    password = "correct horse battery staple"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True


def test_verify_password_rejects_invalid_hash():
    assert verify_password("any password", "not-a-valid-argon2-hash") is False
