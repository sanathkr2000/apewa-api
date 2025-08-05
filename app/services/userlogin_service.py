# import logging
# from fastapi import status
# from starlette.responses import JSONResponse
#
# from app.schema.user_schema import UserLoginResponse
# from app.security import verify_password, create_access_token
# from app.utils.user_utils import fetch_user_by_email
#
# logger = logging.getLogger(__name__)
#
# async def user_login_details(login):
#     logger.debug("Authenticating user", extra={"email": login.user_email})
#
#     user_record = await fetch_user_by_email(login.user_email)
#
#     if not user_record:
#         logger.warning("User not found", extra={"email": login.user_email})
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content=UserLoginResponse(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 message="Invalid credentials"
#             ).model_dump()
#         )
#
#     user = dict(user_record)
#     print("user", user)
#     print("user", user_record)
#
#     # ✅ Password verification
#     if not verify_password(login.user_password, user["password"]):
#         logger.warning("Incorrect password", extra={"email": login.user_email})
#         return JSONResponse(
#             status_code=status.HTTP_403_FORBIDDEN,
#             content=UserLoginResponse(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 message="Invalid credentials"
#             ).model_dump()
#         )
#     token = create_access_token(login.user_email)
#     # ✅ Successful login
#     logger.info("User login successful", extra={"email": login.user_email})
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content=UserLoginResponse(
#             status_code=status.HTTP_200_OK,
#             message="Login successful",
#             userId=user["userId"],
#             token=token,
#             roleId=user["roleId"],
#             firstName=user["firstName"],
#             email=user["email"],
#         ).model_dump()
#     )



import logging
from fastapi import status
from starlette.responses import JSONResponse

from app.db.Departments import departments
from app.db.SubscriptionTypes import subscriptionTypes
from app.db.database import database
from app.schema.user_schema import UserLoginResponse
from app.security import verify_password, create_access_token
from app.utils.user_utils import fetch_user_by_email

logger = logging.getLogger(__name__)

async def user_login_details(login):
    logger.debug("Authenticating user", extra={"email": login.user_email})

    # Fetch user from DB
    user_record = await fetch_user_by_email(login.user_email)

    if not user_record:
        logger.warning("User not found", extra={"email": login.user_email})
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=UserLoginResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Invalid credentials"
            ).model_dump()
        )

    # Convert to dict
    user = dict(user_record)

    try:
        # Password verification
        if not verify_password(login.user_password, user["password"]):
            logger.warning("Incorrect password", extra={"email": login.user_email})
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=UserLoginResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="Invalid credentials"
                ).model_dump()
            )
    except Exception as e:
        logger.exception("Password verification failed", extra={"email": login.user_email})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=UserLoginResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Password verification failed"
            ).model_dump()
        )

    try:
        # FIXED: pass both email and roleId
        token = create_access_token(email=login.user_email, role_id=user["roleId"])
    except Exception as e:
        logger.exception("Token creation failed", extra={"email": login.user_email})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=UserLoginResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Token creation failed"
            ).model_dump()
        )

    # Successful login
    logger.info("User login successful", extra={"email": login.user_email})
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=UserLoginResponse(
            status_code=status.HTTP_200_OK,
            message="Login successful",
            userId=user["userId"],
            token=token,
            roleId=user["roleId"],
            firstName=user["firstName"],
            email=user["email"],
        ).model_dump()
    )


async def get_all_departments_response():
    try:
        # Select only active departments and fetch required columns only
        query = departments.select().with_only_columns(
            departments.c.departmentId,
            departments.c.departmentName
        ).where(departments.c.isActive == 1)

        result = await database.fetch_all(query)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": "Departments fetched successfully",
                "data": [dict(row) for row in result]
            }
        )

    except Exception as e:
        print(f"Error fetching departments: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to fetch departments",
                "data": []
            }
        )


async def get_all_subscription_types_response():
    try:
        # Only fetch required columns and apply filter isActive = 1
        query = subscriptionTypes.select().with_only_columns(
            subscriptionTypes.c.subscriptionTypeId,
            subscriptionTypes.c.subscriptionTypeName,
            subscriptionTypes.c.price
        ).where(subscriptionTypes.c.isActive == 1)

        result = await database.fetch_all(query)

        # Return as list of dicts
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status_code": status.HTTP_200_OK,
                "message": "Subscription types fetched successfully",
                "data": [dict(row) for row in result]
            }
        )
    except Exception as e:
        print(f"Error fetching subscriptions: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to fetch subscription types",
                "data": []
            }
        )