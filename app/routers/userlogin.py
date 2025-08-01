import logging
from fastapi import APIRouter, HTTPException, status

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

# @user_login_router.get("/departments", status_code=status.HTTP_200_OK, tags=["User Login"])
# async def get_departments():
#     try:
#         query = departments.select()
#         return await database.fetch_all(query)
#     except Exception:
#         raise HTTPException(status_code=500, detail="Internal Server Error")
#
# @user_login_router.get("/subscription-types", status_code=status.HTTP_200_OK, tags=["User Login"])
# async def get_subscription_types():
#     try:
#         query = subscriptionTypes.select()
#         return await database.fetch_all(query)
#     except Exception:
#         raise HTTPException(status_code=500, detail="Internal Server Error")



@user_login_router.get("/departments", tags=["User Login"])
async def get_departments():
    return await get_all_departments_response()

@user_login_router.get("/subscription-types", tags=["User Login"])
async def get_subscription_types():
    return await get_all_subscription_types_response()