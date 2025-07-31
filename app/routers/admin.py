from fastapi import APIRouter, Depends

from app.routers.user_routes import user_router
from app.schema.user_schema import RegistrationStatusUpdate
from app.security import get_current_admin_user
from app.services.admin_service import get_all_users_service, update_user_registration_status

admin_router = APIRouter()

@admin_router.get("/api/admin/users", summary="Admin: Get all users")
async def get_all_users():
    return await get_all_users_service(token)


@user_router.put("/users/{user_id}/approve", summary="Approve user registration (Admin only)")
async def approve_user_registration(
    user_id: int,
    data: RegistrationStatusUpdate,
    current_user=Depends(get_current_admin_user)
):
    return await update_user_registration_status(user_id, data.status)
