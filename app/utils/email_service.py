import os
import aiosmtplib
from email.message import EmailMessage
from app.logging_conf import logger
from dotenv import load_dotenv

load_dotenv()  # Load env variables from .env

async def send_email(to: str, subject: str, body: str) -> bool:
    try:
        message = EmailMessage()
        message["From"] = os.getenv("SMTP_SENDER_EMAIL")
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname=os.getenv("SMTP_SERVER"),
            port=int(os.getenv("SMTP_PORT")),
            start_tls=True,
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
        )

        logger.info(f"Email sent successfully to {to}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}", exc_info=True)
        return False
