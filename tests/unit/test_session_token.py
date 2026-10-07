import re

from backend.app.security.session_token import (
    generate_session_token,
    hash_session_token,
)


def test_generate_session_token_returns_nonempty_url_safe_token():
    token = generate_session_token()

    assert token
    assert re.fullmatch(r"[A-Za-z0-9_-]+", token)


def test_generate_session_token_produces_different_tokens():
    first_token = generate_session_token()
    second_token = generate_session_token()

    assert first_token != second_token


def test_hash_session_token_returns_sha256_hex_digest():
    token = "test-session-token"

    token_hash = hash_session_token(token)

    assert token_hash == (
        "7a16f44e82f892c5db994ff1fe2c468656ad31af77ebe04b1d02be3bf8d4cc8e"
    )
    assert len(token_hash) == 64


def test_hash_session_token_is_deterministic():
    token = "test-session-token"

    first_hash = hash_session_token(token)
    second_hash = hash_session_token(token)

    assert first_hash == second_hash
