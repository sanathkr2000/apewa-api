from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.forgot_password_service import send_forgot_password_otp, verify_otp_and_reset_password

forgot_password_router = APIRouter(prefix="/users", tags=["User Profile"])


@forgot_password_router.post("/forgot-password/send-otp", summary="Send OTP for password reset")
async def forgot_password_send_otp(email: str = Form(...)):
    result = await send_forgot_password_otp(email=email)

    # Return consistent response structure
    return JSONResponse(
        status_code=result.get("statusCode", status.HTTP_500_INTERNAL_SERVER_ERROR),
        content={
            "status_code": result.get("statusCode", status.HTTP_500_INTERNAL_SERVER_ERROR),
            "message": result.get("message", "Unknown error"),
            "data": {"userId": result.get("userId")} if result.get("userId") else None
        }
    )



@forgot_password_router.post("/forgot-password/verify-otp", summary="Verify OTP and reset password")
async def forgot_password_verify_otp(
    userId: int = Form(...),
    otp: str = Form(...),
    new_password: str = Form(...)
):
    result = await verify_otp_and_reset_password(user_id=userId, otp=otp, new_password=new_password)

    return JSONResponse(
        status_code=result.get("statusCode", status.HTTP_200_OK),
        content={
            "statusCode": result.get("statusCode", status.HTTP_200_OK),
            "message": result.get("message", "")
        }
    )

