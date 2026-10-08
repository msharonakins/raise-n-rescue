from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.config import settings
from backend.app.schemas.auth import LoginRequest
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

    return {
        "user": {
            "id": str(result.user.id),
            "email": result.user.email,
            "role": result.user.role.value,
        }
    }
