from backend.app.config import Settings


def test_default_session_lifetime_is_24_hours():
    settings = Settings(
        database_host="localhost",
        database_port=5433,
        database_name="raise_n_rescue",
        database_user="test-user",
        database_password="test-password",
    )

    assert settings.session_lifetime_hours == 24
