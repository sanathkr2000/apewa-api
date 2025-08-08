from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.forgot_password_service import forgot_user_password

forgot_password_router = APIRouter(prefix="/users", tags=["User Profile"])

@forgot_password_router.post("/forgot-password", summary="Forgot password - send temporary password to email")
async def forgot_password(email: str = Form(...)):
    try:
        result = await forgot_user_password(email=email)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "Temporary password sent to your email" if result else "Password reset failed"
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "An error occurred during forgot password",
                "error": str(e)
            }
        )
