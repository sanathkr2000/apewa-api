# utils/user_utils.py

import logging
from http.client import HTTPException

from app.db import users
from app.db.Users import userPayments
from app.db.database import database
from app.db.Departments import departments
from app.db.SubscriptionTypes import subscriptionTypes
from sqlalchemy import select
from fastapi import status
from app.schema.user_schema import FetchUserResponse, DepartmentData, SubscriptionTypeData, PaymentData
from sqlalchemy import desc


logger = logging.getLogger(__name__)

async def fetch_user_by_email(email: str):
    logger.debug(f"Fetching user by email: {email}")
    query = users.select().where((users.c.email == email) & (users.c.isActive == True))
    user = await database.fetch_one(query)
    return user

# async def fetch_all_users():
#     query = users.select()
#     return await database.fetch_all(query)


async def fetch_all_users():
    join_query = (
        users
        .join(departments, users.c.departmentId == departments.c.departmentId)
        .join(subscriptionTypes, users.c.subscriptionTypeId == subscriptionTypes.c.subscriptionTypeId)
        .outerjoin(userPayments, userPayments.c.userId == users.c.userId)
    )

    query = (
        select(
            users.c.userId,
            users.c.firstName,
            users.c.lastName,
            users.c.email,
            users.c.phoneNumber,
            users.c.roleId,
            users.c.registrationStatus,
            users.c.isActive,
            users.c.createdAt,
            departments.c.departmentId.label("dept_id"),
            departments.c.departmentName.label("dept_name"),
            subscriptionTypes.c.subscriptionTypeId.label("sub_id"),
            subscriptionTypes.c.subscriptionTypeName.label("sub_name"),
            subscriptionTypes.c.price.label("price"),

            userPayments.c.userPaymentId,
            userPayments.c.paymentEvidence,
            userPayments.c.transactionId,
            userPayments.c.createdAt.label("paymentCreatedAt")
        )
        .select_from(join_query)
        .order_by(desc(users.c.userId))
    )

    try:
        results = await database.fetch_all(query)

        users_data = []
        for row in results:
            user_data = FetchUserResponse(
                userId=row["userId"],
                firstName=row["firstName"],
                lastName=row["lastName"],
                email=row["email"],
                phoneNumber=row["phoneNumber"],
                roleId=row["roleId"],
                registrationStatus=row["registrationStatus"],
                isActive=row["isActive"],
                createdAt=row["createdAt"],
                department=DepartmentData(
                    id=row["dept_id"],
                    name=row["dept_name"]
                ),
                subscriptionType=SubscriptionTypeData(
                    id=row["sub_id"],
                    name=row["sub_name"],
                    price=float(row["price"]) if row["price"] is not None else 0.0
                ),
                payment=PaymentData(
                    userPaymentId=row["userPaymentId"],
                    paymentEvidence=row["paymentEvidence"],
                    transactionId=row["transactionId"],
                    createdAt=row["paymentCreatedAt"]
                ) if row["userPaymentId"] else None
            )

            users_data.append(user_data)

        return users_data

    except Exception as e:
        # Optional: log here instead of returning a JSONResponse
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


# async def fetch_user_by_id(user_id: int):
#     query = (
#         users.join(departments, users.c.departmentId == departments.c.departmentId)
#         .join(subscriptionTypes, users.c.subscriptionTypeId == subscriptionTypes.c.subscriptionTypeId)
#         .select()
#         .where(users.c.userId == user_id)
#     )
#
#     user_data = await database.fetch_one(query)
#
#     if user_data:
#         # Prepare response using UserOut schema
#         user_out = UserOut(
#             userId=user_data["userId"],
#             firstName=user_data["firstName"],
#             lastName=user_data["lastName"],
#             email=user_data["email"],
#             phoneNumber=user_data["phoneNumber"],
#             departmentName=user_data["departmentName"],
#             roleId=user_data["roleId"],  # You can remove this if not needed
#             subscriptionTypeName=user_data["subscriptionTypeName"],
#             registrationStatus=user_data["registrationStatus"],
#             isActive=user_data["isActive"],
#             createdAt=user_data["createdAt"]
#         )
#
#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content=jsonable_encoder({
#                 "status_code": status.HTTP_200_OK,
#                 "message": "User fetched successfully",
#                 "data": user_out
#             })
#         )
#     else:
#         return JSONResponse(
#             status_code=status.HTTP_404_NOT_FOUND,
#             content=jsonable_encoder({
#                 "status_code": status.HTTP_404_NOT_FOUND,
#                 "message": "User not found",
#                 "data": None
#             })
#         )







# async def update_user_registration_status(user_id: int):
#     # Check if the user exists
#     query = users.select().where(users.c.userId == user_id)
#     user = await database.fetch_one(query)
#
#     if not user:
#         return None  # User not found
#
#     # Update only if registrationStatus is 0
#     if user["registrationStatus"] != 0:
#         return "AlreadyUpdated"
#
#     update_query = (
#         users.update()
#         .where(users.c.userId == user_id)
#         .values(registrationStatus=1)
#     )
#
#     await database.execute(update_query)
#     return "Updated"