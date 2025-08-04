import json
import logging
from fastapi import APIRouter, HTTPException, status
from starlette.responses import JSONResponse

from app.schema.user_schema import UserLoginResponse, LoginRequest
from app.services.userlogin_service import user_login_details,get_all_departments_response, get_all_subscription_types_response

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


@user_login_router.get("/departments", tags=["User Login"])
async def get_departments():
    try:
        response = await get_all_departments_response()

        # If it's a FastAPI JSONResponse or similar
        if hasattr(response, 'body'):
            data = json.loads(response.body)
            return {
                "status_code": status.HTTP_200_OK,
                "message": data.get("message", "Departments fetched successfully"),
                "data": data.get("data", [])
            }

        # If it's just raw data (list of departments), no need to decode
        return {
            "status_code": status.HTTP_200_OK,
            "message": "Departments fetched successfully",
            "data": response
        }

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to fetch departments",
                "error": str(e)
            }
        )


@user_login_router.get("/subscriptions", tags=["User Login"])
async def get_subscription_types():
    try:
        response = await get_all_subscription_types_response()

        if hasattr(response, 'body'):
            data = json.loads(response.body)
            return {
                "status_code": status.HTTP_200_OK,
                "message": data.get("message", "Subscription types fetched successfully"),
                "data": data.get("data", [])
            }

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Subscription types fetched successfully",
            "data": response
        }

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to fetch subscription types",
                "error": str(e)
            }
        )