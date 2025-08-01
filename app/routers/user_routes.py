# routers/user_routes

from fastapi import APIRouter, Depends, HTTPException
from app.utils.user_utils import fetch_all_users, fetch_user_by_id
from app.security import get_current_admin_user, get_current_regular_user

user_router = APIRouter()

# Admin: Get all users
@user_router.get(
    "/users",
    summary="Get all users (Admin only)",
    tags=["Admin Users"]
)
async def get_all_users(current_user=Depends(get_current_admin_user)):
    return await fetch_all_users()

# User: Get your own profile
@user_router.get(
    "/users/me",
    summary="Get current user profile",
    tags=["User Profile"]
)
async def get_my_profile(current_user=Depends(get_current_regular_user)):
    return current_user

# User: Get specific user by ID (only your own ID)
@user_router.get(
    "/users/{user_id}",
    summary="Get user by ID (User only)",
    tags=["User Profile"]
)
async def get_user_by_id_route(user_id: int, current_user=Depends(get_current_regular_user)):
    if current_user["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return await fetch_user_by_id(user_id)



# @user_router.put("/users/{user_id}/approve", summary="Approve user registration (Admin only)")
# async def approve_user_registration(user_id: int, current_user=Depends(get_current_admin_user)):
#     result = await update_user_registration_status(user_id)
#
#     if result is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     elif result == "AlreadyUpdated":
#         raise HTTPException(status_code=400, detail="User already approved")
#
#     return {"
#
#     message": "User registration approved successfully"}


# @user_router.put("/users/{user_id}/approve", summary="Approve user registration (Admin only)")
# async def approve_user_registration(
#     user_id: int,
#     data: RegistrationStatusUpdate,
#     current_user=Depends(get_current_admin_user)
# ):
#     return await update_user_registration_status(user_id, data.status)


