# routers/user_routes

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status

from app.db.Departments import departments
from app.db.SubscriptionTypes import subscriptionTypes
from app.db.database import database
from app.logging_conf import logger
from app.schema.user_schema import UserOut
from app.utils.user_utils import fetch_all_users, fetch_user_by_id
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
        # Ensure this returns a list of dicts or Pydantic models
        users = await fetch_all_users()

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Active users fetched successfully",
            "data": users
        }

    except HTTPException as http_exc:
        logger.warning(f"HTTP error in get_all_users: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"Unexpected error in get_all_users: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# User: Get your own profile
@user_router.get(
    "/users/me",
    summary="Get current user profile",
    tags=["User Profile"]
)
async def get_my_profile(current_user=Depends(get_current_regular_user)):
    try:
        user = dict(current_user)

        # Fetch department name
        dept_query = departments.select().where(departments.c.departmentId == user["departmentId"])
        dept_record = await database.fetch_one(dept_query)
        department_name = dept_record["departmentName"] if dept_record else "Unknown"

        # Fetch subscription type name
        sub_query = subscriptionTypes.select().where(subscriptionTypes.c.subscriptionTypeId == user["subscriptionTypeId"])
        sub_record = await database.fetch_one(sub_query)
        subscription_type_name = sub_record["subscriptionTypeName"] if sub_record else "Unknown"

        user_data = UserOut(
            userId=user["userId"],
            firstName=user["firstName"],
            lastName=user["lastName"],
            email=user["email"],
            phoneNumber=user["phoneNumber"],
            departmentName=department_name,
            roleId=user["roleId"],
            subscriptionTypeName=subscription_type_name,
            registrationStatus=user["registrationStatus"],
            isActive=user["isActive"],
            createdAt=user["createdAt"]
        )

        return {
            "status_code": status.HTTP_200_OK,
            "message": "User fetched successfully",
            "data": user_data.dict()
        }

    except KeyError as ke:
        return {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": f"Missing expected key in user data: {str(ke)}"
        }

    except Exception as e:
        # Optionally log the exception using logger.exception("...")
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An error occurred while fetching the profile",
            "error": str(e)
        }

@user_router.get(
    "/users/{user_id}",
    summary="Get user by ID (User only)",
    tags=["User Profile"]
)
async def get_user_by_id_route(user_id: int, current_user=Depends(get_current_regular_user)):
    try:
        if current_user["userId"] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Handle JSONResponse directly
        return await fetch_user_by_id(user_id)

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Unexpected error in get_user_by_id_route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")




# @user_router.put("/users/{user_id}/approve", summary="Approve user registration (Admin only)")
# async def approve_user_registration(user_id: int, current_user=Depends(get_current_admin_user)):
#     result = await update_user_registration_status(user_id)
#
#     if result is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     elif result == "AlreadyUpdated":
#         raise HTTPException(status_code=400, detail="User already approved")
#
#     return {"
#
#     message": "User registration approved successfully"}


# @user_router.put("/users/{user_id}/approve", summary="Approve user registration (Admin only)")
# async def approve_user_registration(
#     user_id: int,
#     data: RegistrationStatusUpdate,
#     current_user=Depends(get_current_admin_user)
# ):
#     return await update_user_registration_status(user_id, data.status)


