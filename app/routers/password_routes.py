from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse
from app.services.password_service import reset_user_password
from app.security import get_current_regular_user, get_current_admin_or_regular_user

password_router = APIRouter()

@password_router.put(
    "/users/reset-password",
    summary="Reset user password",
    tags=["User Profile"]
)
async def reset_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    # current_user=Depends(get_current_regular_user)
    current_user=Depends(get_current_admin_or_regular_user)  # changed here

):
    if isinstance(current_user, JSONResponse):
        return current_user

    try:
        result = await reset_user_password(
            user=current_user,
            current_password=current_password,
            new_password=new_password
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "Password updated successfully" if result else "Password update failed"
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "An error occurred during password reset",
                "error": str(e)
            }
        )
