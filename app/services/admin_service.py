# service/admin_service

import logging
import json
from typing import Optional

from fastapi import status, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.db import users
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


async def update_user_registration_status(user_id: int, is_approved: bool):
    try:
        query = users.select().where(users.c.userId == user_id)
        user = await database.fetch_one(query)

        if not user:
            logger.warning(f"User with ID {user_id} not found.")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status_code": 404,
                    "message": f"User with ID {user_id} not found"
                }
            )

        #  Check if user is active
        if not user["isActive"]:
            logger.warning(f"User with ID {user_id} is not active. Registration status not updated.")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "status_code": 403,
                    "message": "Cannot update registration status for inactive user"
                }
            )

        new_status = 1 if is_approved else 0

        if user["registrationStatus"] == new_status:
            logger.info(f"User with ID {user_id} already has registrationStatus={new_status}.")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status_code": 400,
                    "message": f"User is already {'approved' if is_approved else 'not approved'}"
                }
            )

        update_query = (
            users.update()
            .where(users.c.userId == user_id)
            .values(registrationStatus=new_status)
        )
        await database.execute(update_query)
        logger.info(f"User registrationStatus updated to {new_status} for user_id={user_id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": f"User registration {'approved' if is_approved else 'disapproved'} successfully"
            }
        )

    except Exception as e:
        logger.exception("Error occurred while updating user registration status")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "Internal Server Error",
                "error": str(e)
            }
        )



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
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status_code": 404, "message": f"User ID {user_id} not found"}
            )

        if user["isActive"] == is_active:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status_code": 400,
                    "message": f"User is already {'active' if is_active else 'inactive'}"
                }
            )

        update_query = (
            users.update()
            .where(users.c.userId == user_id)
            .values(isActive=is_active)
        )
        await database.execute(update_query)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": f"User has been {'reactivated' if is_active else 'deactivated'} successfully"
            }
        )

    except Exception as e:
        logger.exception("Error updating user active status")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status_code": 500, "message": "Internal Server Error", "error": str(e)}
        )