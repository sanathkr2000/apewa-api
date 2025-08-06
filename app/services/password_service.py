from fastapi import HTTPException, status
from app.db.Users import users
from app.db.database import database
from app.logging_conf import logger
from app.security import verify_password, hash_password

async def reset_user_password(user: dict, current_password: str, new_password: str) -> bool:
    try:
        user_id = user["userId"]

        # Step 1: Fetch user's existing hashed password
        query = users.select().where(users.c.userId == user_id)
        db_user = await database.fetch_one(query)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found"
                }
            )

        # Step 2: Verify current password
        if not verify_password(current_password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Current password is incorrect"
                }
            )

        # Step 3: Reject if new password is same as current password
        if verify_password(new_password, db_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "New password must be different from the current password"
                }
            )

        # Step 4: Hash new password
        hashed_new_password = hash_password(new_password)

        # Step 5: Update DB
        update_query = (
            users.update()
            .where(users.c.userId == user_id)
            .values(password=hashed_new_password)
        )
        await database.execute(update_query)

        return True

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        logger.error(f"Unexpected error resetting password for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error while resetting password"
            }
        )
