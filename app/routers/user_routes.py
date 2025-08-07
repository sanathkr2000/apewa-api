# routers/user_routes

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import desc

from app.db.Departments import departments
from app.db.SubscriptionTypes import subscriptionTypes
from app.db.Users import userPayments
from app.db.database import database
from app.db.registrationStatus import registrationStatus
from app.logging_conf import logger
from app.schema.user_schema import UserOut
# from app.services.userlogin_service import fetch_user_by_id
from app.utils.user_utils import fetch_all_users
from app.security import get_current_admin_user, get_current_regular_user

user_router = APIRouter()

# Admin: Get all users
@user_router.get(
    "/users",
    summary="Get all users (Admin only)",
    tags=["Admin Users"]
)
async def get_all_users(current_user=Depends(get_current_admin_user)):
    try:
        # Handle the case when user is not admin
        if isinstance(current_user, JSONResponse):
            return current_user

        # Otherwise, continue with logic
        users = await fetch_all_users()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "Active users fetched successfully",
                "data": jsonable_encoder(users)
            }
        )

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": f"Failed to fetch users: {str(e)}",
                "data": []
            }
        )

# User: Get your own profile
@user_router.get(
    "/users/me",
    summary="Get current user profile",
    tags=["User Profile"]
)
async def get_my_profile(current_user=Depends(get_current_regular_user)):
    if isinstance(current_user, JSONResponse):
        return current_user  # Return 403 if unauthorized

    try:
        user = dict(current_user)

        # Fetch department name
        department_name = "Unknown"
        if user.get("departmentId"):
            dept_query = departments.select().where(departments.c.departmentId == user["departmentId"])
            dept_record = await database.fetch_one(dept_query)
            if dept_record:
                department_name = dept_record["departmentName"]

        # Fetch registration status name
        registration_status = None
        if user.get("registrationStatusId"):
            reg_status_query = registrationStatus.select().where(
                registrationStatus.c.registrationStatusId == user["registrationStatusId"]
            )
            reg_status_record = await database.fetch_one(reg_status_query)
            if reg_status_record:
                registration_status = reg_status_record["statusName"]

        # Fetch latest user payment for subscription details
        payment_query = (
            userPayments
            .select()
            .where(userPayments.c.userId == user["userId"])
            .order_by(desc(userPayments.c.createdAt))
            .limit(1)
        )
        payment_record = await database.fetch_one(payment_query)

        # Defaults
        subscription_type_name = "Unknown"
        subscription_start_date = None
        subscription_end_date = None

        if payment_record:
            subscription_type_id = payment_record["subscriptionTypeId"]
            subscription_start_date = payment_record["subscriptionStartDate"]
            subscription_end_date = payment_record["subscriptionEndDate"]

            if subscription_type_id:
                sub_query = subscriptionTypes.select().where(
                    subscriptionTypes.c.subscriptionTypeId == subscription_type_id
                )
                sub_record = await database.fetch_one(sub_query)
                if sub_record:
                    subscription_type_name = sub_record["subscriptionTypeName"]

        # Build user response
        user_data = UserOut(
            userId=user["userId"],
            firstName=user["firstName"],
            lastName=user["lastName"],
            email=user["email"],
            phoneNumber=user["phoneNumber"],
            departmentName=department_name,
            roleId=user["roleId"],
            subscriptionTypeName=subscription_type_name,
            registrationStatus=registration_status,
            isActive=user["isActive"],
            createdAt=user["createdAt"],
            subscriptionStartDate=subscription_start_date,
            subscriptionEndDate=subscription_end_date
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": 200,
                "message": "User fetched successfully",
                "data": jsonable_encoder(user_data)
            }
        )

    except KeyError as ke:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status_code": 400,
                "message": f"Missing expected key in user data: {str(ke)}"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "An error occurred while fetching the profile",
                "error": str(e)
            }
        )


# @user_router.get(
#     "/users/{user_id}",
#     summary="Get user by ID (User only)",
#     tags=["User Profile"]
# )
# async def get_user_by_id_route(user_id: int, current_user=Depends(get_current_regular_user)):
#     if isinstance(current_user, JSONResponse):
#         return current_user  # Return 403 response
#
#     try:
#         if current_user["userId"] != user_id:
#             return JSONResponse(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 content={
#                     "status_code": status.HTTP_403_FORBIDDEN,
#                     "message": "Access denied"
#                 }
#             )
#
#         return await fetch_user_by_id(user_id)
#
#     except Exception as e:
#         logger.error(f"Unexpected error in get_user_by_id_route: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={
#                 "status_code": 500,
#                 "message": "Internal Server Error"
#             }
#         )


