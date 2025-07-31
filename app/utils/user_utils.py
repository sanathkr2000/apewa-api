import logging
from app.db import users
from app.db.database import database

logger = logging.getLogger(__name__)

async def fetch_user_by_email(email: str):
    logger.debug(f"Fetching user by email: {email}")
    query = users.select().where((users.c.email == email) & (users.c.isActive == True))
    user = await database.fetch_one(query)
    return user

async def fetch_all_users():
    query = users.select()
    return await database.fetch_all(query)

async def fetch_user_by_id(user_id: int):
    query = users.select().where(users.c.userId == user_id)
    return await database.fetch_one(query)


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