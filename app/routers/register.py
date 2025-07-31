from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from app.services import register_service
from app.schema.user_schema import UserRegisterResponse
import logging

logger = logging.getLogger("app.register")

register_router = APIRouter()

@register_router.post("/", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_with_payment(
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phoneNumber: str = Form(...),
    departmentId: int = Form(...),
    roleId: int = Form(...),
    subscriptionTypeId: int = Form(...),
    transactionId: Optional[str] = Form(None),
    paymentEvidence: Optional[UploadFile] = File(None),  # ✅ Optional File
):
    user_data = {
        "firstName": firstName,
        "lastName": lastName,
        "email": email,
        "password": password,
        "phoneNumber": phoneNumber,
        "departmentId": departmentId,
        "roleId": roleId,
        "subscriptionTypeId": subscriptionTypeId
    }

    try:
        logger.info("Register API called for email: %s", email)
        response = await register_service.register_user_with_payment_core(
            user_data=user_data,
            paymentEvidence=paymentEvidence,
            transactionId=transactionId
        )
        return response  # Already a JSONResponse in service layer

    except HTTPException as http_exc:
        logger.warning("HTTPException during registration: %s", http_exc.detail)
        raise http_exc

    except Exception as exc:
        logger.exception("Unexpected error during registration for email: %s", email)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error during registration"
            }
        )
