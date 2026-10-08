from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    get_current_user,
    get_db,
    require_csrf_token,
)
from backend.app.config import settings
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest
from backend.app.security.csrf import generate_csrf_token
from backend.app.services.authentication_errors import AuthenticationError
from backend.app.services.authentication_service import AuthenticationService

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login")
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    service = AuthenticationService(db)

    try:
        result = service.authenticate(
            email=request.email,
            password=request.password,
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    response.set_cookie(
        key="session",
        value=result.session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.session_lifetime_hours * 60 * 60,
        path="/",
    )

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=generate_csrf_token(),
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=settings.session_lifetime_hours * 60 * 60,
        path="/",
    )

    return {
        "user": {
            "id": str(result.user.id),
            "email": result.user.email,
            "role": result.user.role.value,
        }
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value,
        }
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    _: None = Depends(require_csrf_token),
    session_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE_NAME,
    ),
    db: Session = Depends(get_db),
):
    if session_token is not None:
        service = AuthenticationService(db)

        try:
            service.revoke_session(session_token)
        except AuthenticationError:
            pass

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        httponly=False,
        secure=False,
        samesite="lax",
    )
