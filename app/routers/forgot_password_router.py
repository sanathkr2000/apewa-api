# forgot_password_router.py

from fastapi import APIRouter, Form, status
from fastapi.responses import JSONResponse
from app.services.forgot_password_service import send_forgot_password_otp, verify_otp, reset_password

forgot_password_router = APIRouter(prefix="/users", tags=["User Profile"])


@forgot_password_router.post("/forgot-password/send-otp", summary="Send OTP for password reset")
async def forgot_password_send_otp(email: str = Form(...)):
    result = await send_forgot_password_otp(email=email)
    return JSONResponse(
        status_code=result.get("statusCode", status.HTTP_500_INTERNAL_SERVER_ERROR),
        content={
            "status_code": result.get("statusCode", status.HTTP_500_INTERNAL_SERVER_ERROR),
            "message": result.get("message", "Unknown error"),
            "data": {"userId": result.get("userId")} if result.get("userId") else None
        }
    )


@forgot_password_router.post("/forgot-password/verify-otp", summary="Verify OTP")
async def forgot_password_verify_otp(userId: int = Form(...), otp: str = Form(...)):
    result = await verify_otp(user_id=userId, otp=otp)
    return JSONResponse(
        status_code=result.get("statusCode", status.HTTP_200_OK),
        content={
            "status_code": result.get("statusCode", status.HTTP_200_OK),
            "message": result.get("message", "")
        }
    )


@forgot_password_router.post("/forgot-password/reset-password", summary="Reset password")
async def forgot_password_reset_password(userId: int = Form(...), new_password: str = Form(...)):
    result = await reset_password(user_id=userId, new_password=new_password)
    return JSONResponse(
        status_code=result.get("statusCode", status.HTTP_200_OK),
        content={
            "status_code": result.get("statusCode", status.HTTP_200_OK),
            "message": result.get("message", "")
        }
    )

