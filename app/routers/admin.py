from http.client import HTTPException

from fastapi import APIRouter, Depends
from rich import status
from starlette.responses import JSONResponse

from app.routers.user_routes import user_router
from app.schema.user_schema import RegistrationStatusUpdate, UserUpdateRequest, UserActiveStatusUpdate
from app.security import get_current_admin_user, get_current_regular_user
from app.services.admin_service import get_all_users_service, update_user_registration_status, update_user_details,update_user_active_status_service

admin_router = APIRouter()

# @admin_router.get("/api/admin/users", summary="Admin: Get all users")
# async def get_all_users():
#     return await get_all_users_service(token)


@user_router.put(
    "/users/{user_id}/approve",
    summary="Approve user registration (Admin only)",
    tags=["Admin Users"]
)
async def approve_user_registration(
    user_id: int,
    data: RegistrationStatusUpdate,
    current_user=Depends(get_current_admin_user)
):
    return await update_user_registration_status(user_id, data.status)



@user_router.put(
    "/users/me",
    summary="Update your own profile (User only)",
    tags=["User Profile"]
)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user=Depends(get_current_regular_user)
):
    if isinstance(current_user, JSONResponse):
        return current_user  # Return 403 response

    user_id = current_user["userId"]
    update_dict = update_data.dict(exclude_unset=True)

    if not update_dict:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "No fields provided for update"
            }
        )

    result = await update_user_details(user_id, update_dict)

    return JSONResponse(
        status_code=result["status_code"],
        content=result
    )


# @admin_router.put(
#     "/users/{user_id}/active-status",
#     summary="Admin: Update user's active status (soft delete / reactivate)",
#     tags=["Admin Users"]
# )

@admin_router.put(
    "/users/{user_id}/status",  # 👈 New clean path
    summary="Admin: Update user's active status",
    tags=["Admin Users"]
)
async def update_user_active_status(
    user_id: int,
    payload: UserActiveStatusUpdate,
    current_user=Depends(get_current_admin_user)
):
    return await update_user_active_status_service(user_id, payload.isActive)

