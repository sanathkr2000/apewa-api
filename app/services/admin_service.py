# service/admin_service

import logging
import json
from datetime import timedelta, datetime, timezone
from typing import Optional

from fastapi import status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.db import users
from app.db.Users import userPayments
from app.db.database import database
from app.schema.user_schema import UserOut
from app.utils.user_utils import fetch_all_users  # Make sure this accepts a token

logger = logging.getLogger(__name__)

async def get_all_users_service(authorization: str = Header(...)):
    try:
        # Extract token from Authorization header (format: "Bearer <token>")
        if not authorization.startswith("Bearer "):
            raise ValueError("Invalid Authorization header format")

        token = authorization.split(" ")[1]

        # Fetch all users (token-based validation inside fetch_all_users)
        users_list = await fetch_all_users(token)

        # Convert DB rows to Pydantic models and then to JSON serializable dicts
        users_data = [UserOut(**dict(user)) for user in users_list]
        json_ready_data = jsonable_encoder(users_data)

        # Return structured response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "User list fetched successfully",
                "data": json_ready_data
            }
        )

    except ValueError as ve:
        logger.warning("Authorization Error: %s", ve)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status_code": 401,
                "message": str(ve)
            }
        )

    except Exception as e:
        logger.exception("Error in get_all_users_service")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "Internal Server Error",
                "error": str(e)
            }
        )


UTC = timezone.utc  # Ensure this is defined

async def update_user_registration_status(user_id: int, registration_status_id):
    try:
        # 🔧 Ensure registration_status_id is an integer
        registration_status_id = int(registration_status_id)

        print(f"Fetching user with ID: {user_id}")
        logger.info(f"Fetching user with ID: {user_id}")

        # Step 1: Get user
        user_query = users.select().where(users.c.userId == user_id)
        user = await database.fetch_one(user_query)

        if not user:
            message = f"User with ID {user_id} not found"
            logger.warning(message)
            return JSONResponse(status_code=404, content={"status_code": 404, "message": message})

        if not user["isActive"]:
            message = f"User {user_id} is inactive"
            logger.warning(message)
            return JSONResponse(status_code=403, content={"status_code": 403, "message": message})

        # ⚠️ Check if already approved
        current_status = user["registrationStatusId"]
        if current_status == 3 and registration_status_id == 3:
            message = "User is already approved. No further action taken."
            logger.info(message)
            return JSONResponse(status_code=409, content={"status_code": 409, "message": message})

        # Step 2: Update registrationStatusId in users table
        await database.execute(
            users.update()
            .where(users.c.userId == user_id)
            .values(registrationStatusId=registration_status_id)
        )

        # Step 3: Handle subscription updates based on status change
        payment_query = (
            userPayments.select()
            .where(userPayments.c.userId == user_id)
            .order_by(userPayments.c.createdAt.desc())
        )
        user_payment = await database.fetch_one(payment_query)

        if not user_payment:
            message = f"No userPayments record found for user_id: {user_id}"
            logger.warning(message)
            return JSONResponse(status_code=404, content={"status_code": 404, "message": message})

        # CASE 1: 2 → 3
        if current_status == 2 and registration_status_id == 3:
            start_date = datetime.now(UTC)
            subscription_type_id = user_payment["subscriptionTypeId"]

            if subscription_type_id == 1:  # Lifetime
                end_date = None
            elif subscription_type_id == 2:  # Yearly
                end_date = start_date + timedelta(days=365)
            else:
                message = f"Invalid subscriptionTypeId: {subscription_type_id}"
                logger.error(message)
                return JSONResponse(status_code=400, content={"status_code": 400, "message": message})

            await database.execute(
                userPayments.update()
                .where(userPayments.c.userPaymentId == user_payment["userPaymentId"])
                .values(subscriptionStartDate=start_date, subscriptionEndDate=end_date)
            )

            message = "User approved: subscription dates set"
            logger.info(message)
            return JSONResponse(status_code=200, content={
                "status_code": 200,
                "message": message,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None
            })

        # CASE 2: 3 → 2
        elif current_status == 3 and registration_status_id == 2:
            await database.execute(
                userPayments.update()
                .where(userPayments.c.userPaymentId == user_payment["userPaymentId"])
                .values(subscriptionStartDate=None, subscriptionEndDate=None)
            )

            message = "User status downgraded: subscription dates cleared"
            logger.info(message)
            return JSONResponse(status_code=200, content={
                "status_code": 200,
                "message": message
            })

        # OTHER STATUS CHANGES
        else:
            message = f"Registration status updated for user_id: {user_id}"
            logger.info(message)
            return JSONResponse(status_code=200, content={
                "status_code": 200,
                "message": message
            })

    except Exception as e:
        logger.exception("Error updating registration status")
        return JSONResponse(status_code=500, content={
            "status_code": 500,
            "message": "Internal server error",
            "error": str(e)
        })



async def update_user_details(user_id: int, user_data: dict):
    # Update the user
    query = users.update().where(users.c.userId == user_id).values(**user_data)
    result = await database.execute(query)

    if result:  # If update affected rows
        return {
            "status_code": status.HTTP_200_OK,
            "message": "User details updated successfully",
            "updated_fields": user_data  # Show only changed fields
        }
    else:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "message": "User not found or no changes made",
            "updated_fields": {}
        }


async def update_user_active_status_service(user_id: int, is_active: bool):
    try:
        query = users.select().where(users.c.userId == user_id)
        user = await database.fetch_one(query)

        if not user:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": f"User ID {user_id} not found"
            }

        if user["isActive"] == is_active:
            return {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": f"User is already {'active' if is_active else 'inactive'}"
            }

        update_query = (
            users.update()
            .where(users.c.userId == user_id)
            .values(isActive=is_active)
        )
        await database.execute(update_query)

        return {
            "status_code": status.HTTP_200_OK,
            "message": f"User has been {'reactivated' if is_active else 'deactivated'} successfully"
        }

    except Exception as e:
        logger.exception("Error updating user active status")
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal Server Error",
            "error": str(e)
        }