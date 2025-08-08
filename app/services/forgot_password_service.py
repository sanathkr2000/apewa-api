from fastapi import HTTPException, status
from app.db.Users import users
from app.db.database import database
from app.logging_conf import logger
from app.security import hash_password
import secrets
import string
from app.utils.email_service import send_email

async def forgot_user_password(email: str) -> bool:
    try:
        # Step 1: Check if user exists
        query = users.select().where(users.c.email == email)
        db_user = await database.fetch_one(query)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with this email"
            )

        # Step 2: Generate temporary password
        temp_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

        # Step 3: Hash the temporary password
        hashed_temp_password = hash_password(temp_password)

        # Step 4: Update DB
        update_query = (
            users.update()
            .where(users.c.userId == db_user["userId"])
            .values(password=hashed_temp_password)
        )
        await database.execute(update_query)

        # Step 5: Send email
        subject = "Password Reset - Temporary Password"
        body = (
            f"Hello {db_user['firstName']},\n\n"
            f"Your password has been reset. Here is your temporary password:\n\n"
            f"{temp_password}\n\n"
            f"Please log in and change your password.\n\n"
            f"Regards,\nSupport Team"
        )

        email_sent = await send_email(to=email, subject=subject, body=body)

        return email_sent

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        logger.error(f"Unexpected error during forgot password: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing forgot password"
        )
