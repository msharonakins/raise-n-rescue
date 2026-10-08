import hmac
import secrets


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def verify_csrf_token(expected_token: str, provided_token: str) -> bool:
    return hmac.compare_digest(expected_token, provided_token)
