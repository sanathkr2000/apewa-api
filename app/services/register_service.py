# import os
# from datetime import datetime
# from passlib.hash import bcrypt
# from sqlalchemy import insert, select
# from app.db.Users import users, userPayments
# from app.db.database import database
# from fastapi import status
# from fastapi.responses import JSONResponse
# import logging
#
# logger = logging.getLogger("app.register")
#
# UPLOAD_DIR = "uploads/payment_proofs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)
#
# async def register_user_with_payment_core(user_data: dict, paymentEvidence, transactionId: str = None):
#     email = user_data.get("email", "-")
#     try:
#         logger.info("Starting registration process", extra={"email": email})
#
#         # Check if user exists
#         query = select(users).where(users.c.email == email)
#         existing = await database.fetch_one(query)
#         if existing:
#             logger.warning("User already exists", extra={"email": email})
#             return JSONResponse(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 content={
#                     "statusCode": status.HTTP_400_BAD_REQUEST,
#                     "message": "User already exists with this email"
#                 }
#             )
#
#         # Hash password
#         hashed_password = bcrypt.hash(user_data["password"])
#         logger.debug("Password hashed", extra={"email": email})
#
#         # Insert user
#         query = insert(users).values(
#             firstName=user_data["firstName"],
#             lastName=user_data["lastName"],
#             email=email,
#             password=hashed_password,
#             phoneNumber=user_data["phoneNumber"],
#             departmentId=user_data["departmentId"],
#             roleId=user_data["roleId"],
#             subscriptionTypeId=user_data["subscriptionTypeId"],
#             registrationStatus=False,
#             isActive=True,
#             createdAt=datetime.utcnow()
#         )
#         user_id = await database.execute(query)
#         logger.info("User inserted", extra={"email": email, "userId": user_id})
#
#         # Save file
#         filename = f"{user_id}_{paymentEvidence.filename}"
#         file_path = os.path.join(UPLOAD_DIR, filename)
#         with open(file_path, "wb") as f:
#             f.write(await paymentEvidence.read())
#         logger.debug("Payment proof uploaded", extra={"userId": user_id, "uploadedFileName": filename})
#
#         # Insert payment
#         await database.execute(
#             insert(userPayments).values(
#                 userId=user_id,
#                 paymentEvidence=filename,
#                 transactionId=transactionId,
#                 isActive=True,
#                 createdAt=datetime.utcnow()
#             )
#         )
#         logger.info("Payment record inserted", extra={"userId": user_id, "transactionId": transactionId})
#
#         return JSONResponse(
#             status_code=status.HTTP_201_CREATED,
#             content={
#                 "statusCode": status.HTTP_201_CREATED,
#                 "message": "User registration successful",
#                 "userId": user_id
#             }
#         )
#
#     except Exception:
#         logger.exception("Error during user registration", extra={"email": email})
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={
#                 "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": "An unexpected error occurred during registration"
#             }
#         )



import os
import re
from datetime import datetime
from passlib.hash import bcrypt
from sqlalchemy import insert, select
from app.db.Users import users, userPayments
from app.db.database import database
from fastapi import status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("app.register")

UPLOAD_DIR = "uploads/payment_proofs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def register_user_with_payment_core(user_data: dict, paymentEvidence, transactionId: str = None):
    email = user_data.get("email", "-")
    try:
        logger.info("Starting registration process", extra={"email": email})

        # Check if user already exists
        query = select(users).where(users.c.email == email)
        existing = await database.fetch_one(query)
        if existing:
            logger.warning("User already exists", extra={"email": email})
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "User already exists with this email"
                }
            )

        # Hash the password
        hashed_password = bcrypt.hash(user_data["password"])
        logger.debug("Password hashed", extra={"email": email})

        # Insert user
        query = insert(users).values(
            firstName=user_data["firstName"],
            lastName=user_data["lastName"],
            email=email,
            password=hashed_password,
            phoneNumber=user_data["phoneNumber"],
            departmentId=user_data["departmentId"],
            roleId=user_data["roleId"],
            subscriptionTypeId=user_data["subscriptionTypeId"],
            registrationStatus=False,
            isActive=True,
            createdAt=datetime.utcnow()
        )
        user_id = await database.execute(query)
        logger.info("User inserted", extra={"email": email, "userId": user_id})

        # Save payment evidence file (if present)
        filename = None
        if paymentEvidence:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

            original_name = paymentEvidence.filename.replace(" ", "_")
            base_name, ext = os.path.splitext(original_name)
            base_name = re.sub(r'\W+', '', base_name).strip()  # sanitize base name

            filename = f"{base_name}_{timestamp}{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(await paymentEvidence.read())
            logger.debug("Payment proof uploaded", extra={"userId": user_id, "uploadedFileName": filename})
        else:
            logger.info("No payment evidence uploaded", extra={"userId": user_id})

        # Insert payment details (file is optional)
        await database.execute(
            insert(userPayments).values(
                userId=user_id,
                paymentEvidence=filename,
                transactionId=transactionId,
                isActive=True,
                createdAt=datetime.utcnow()
            )
        )
        logger.info("Payment record inserted", extra={"userId": user_id, "transactionId": transactionId})

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "statusCode": status.HTTP_201_CREATED,
                "message": "User registration successful",
                "userId": user_id
            }
        )

    except Exception:
        logger.exception("Error during user registration", extra={"email": email})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred during registration"
            }
        )
