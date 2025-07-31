import logging
from fastapi import APIRouter, HTTPException, status
from app.schema.user_schema import UserLoginResponse, LoginRequest
from app.services.userlogin_service import user_login_details

logger = logging.getLogger(__name__)

user_login_router = APIRouter()

@user_login_router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login_user(login: LoginRequest):
    try:
        return await user_login_details(login)
    except HTTPException as e:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during login"
        )
