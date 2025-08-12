# forgot_password_service.py
from zoneinfo import ZoneInfo  # Requires Python 3.9+ and tzdata installed

from fastapi import status
from datetime import datetime, timedelta, timezone
import secrets
import os

from app.db.Users import users
from app.db.PasswordResetOtp import passwordResetOtp
from app.db.database import database
from app.logging_conf import logger
from app.security import hash_password
from app.utils.email_service import send_email


async def send_forgot_password_otp(email: str) -> dict:
    try:
        query = users.select().where(users.c.email == email)
        db_user = await database.fetch_one(query)

        if not db_user:
            return {
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User not found with this email"
            }

        # Check if user is active
        if db_user["isActive"] != 1:
            return {
                "statusCode": status.HTTP_403_FORBIDDEN,
                "message": "User is deactivated. Cannot send OTP."
            }

        otp_code = str(secrets.randbelow(1000000)).zfill(6)
        OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES"))
        expiry_time = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

        insert_query = passwordResetOtp.insert().values(
            userId=db_user["userId"],
            otpCode=otp_code,
            expiryTime=expiry_time,
            isUsed=False
        )
        await database.execute(insert_query)

        subject = "Password Reset OTP"
        body_text = f"Hello {db_user['firstName']},\nYour OTP is: {otp_code}\nIt will expire in {OTP_EXPIRY_MINUTES} minutes."
        body_html = f"<p>Hello {db_user['firstName']},</p><p>Your OTP is:</p><h2>{otp_code}</h2><p>It will expire in {OTP_EXPIRY_MINUTES} minutes.</p>"

        email_sent = send_email(
            to_email=email,
            to_name=db_user["firstName"],
            subject=subject,
            body_html=body_html,
            body_text=body_text
        )

        if not email_sent:
            return {
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to send OTP email"
            }

        return {
            "statusCode": status.HTTP_200_OK,
            "message": "OTP sent to email",
            "userId": db_user["userId"]
        }

    except Exception as e:
        logger.error(f"Error sending forgot password OTP: {e}", exc_info=True)
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error"
        }


async def verify_otp(user_id: int, otp: str) -> dict:
    try:
        otp_query = (
            passwordResetOtp.select()
            .where(passwordResetOtp.c.userId == user_id)
            .where(passwordResetOtp.c.otpCode == otp)
            .where(passwordResetOtp.c.isUsed == False)
        )
        db_otp = await database.fetch_one(otp_query)

        if not db_otp:
            return {
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid OTP"
            }

        if datetime.utcnow() > db_otp["expiryTime"]:
            return {
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "OTP expired"
            }

        # Mark OTP as used
        update_otp_query = (
            passwordResetOtp.update()
            .where(passwordResetOtp.c.otpId == db_otp["otpId"])
            .values(isUsed=True)
        )
        await database.execute(update_otp_query)

        return {
            "statusCode": status.HTTP_200_OK,
            "message": "OTP verified successfully"
        }

    except Exception as e:
        logger.error(f"Error verifying OTP: {e}", exc_info=True)
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error"
        }


async def reset_password(user_id: int, new_password: str) -> dict:
    try:
        # Check user exists
        query = users.select().where(users.c.userId == user_id)
        db_user = await database.fetch_one(query)
        if not db_user:
            return {
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User not found"
            }

        hashed_password = hash_password(new_password)

        update_user_query = (
            users.update()
            .where(users.c.userId == user_id)
            .values(password=hashed_password)
        )
        await database.execute(update_user_query)

        return {
            "statusCode": status.HTTP_200_OK,
            "message": "Password reset successful"
        }

    except Exception as e:
        logger.error(f"Error resetting password: {e}", exc_info=True)
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error"
        }
