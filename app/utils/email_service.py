# # emial_service.py
#
# import os
# import requests
# from dotenv import load_dotenv
#
# load_dotenv()
#
# ZEPTO_API_URL = os.getenv("ZEPTO_API_URL")
# ZEPTO_API_KEY = os.getenv("ZEPTO_API_KEY")  # raw key only
# ZEPTO_FROM_ADDRESS = os.getenv("ZEPTO_FROM_ADDRESS")
# ZEPTO_FROM_NAME = os.getenv("ZEPTO_FROM_NAME")
#
#
# def send_email(to_email: str, to_name: str, subject: str, body_html: str, body_text: str = None) -> bool:
#     """Send email via ZeptoMail API"""
#     try:
#         payload = {
#             "from": {
#                 "address": ZEPTO_FROM_ADDRESS,
#                 "name": ZEPTO_FROM_NAME
#             },
#             "to": [
#                 {
#                     "email_address": {
#                         "address": to_email,
#                         "name": to_name
#                     }
#                 }
#             ],
#             "subject": subject,
#             "htmlbody": body_html
#         }
#
#         if body_text:
#             payload["textbody"] = body_text
#
#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#             "Authorization": f"Zoho-enczapikey {ZEPTO_API_KEY}"  # prepend here
#         }
#
#         response = requests.post(ZEPTO_API_URL, json=payload, headers=headers)
#         response.raise_for_status()
#         return True
#
#     except requests.exceptions.HTTPError as http_err:
#         print(f"HTTP error while sending email: {http_err} - {response.text}")
#         return False
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return False
#



# emial_service.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

ZEPTO_SMTP_USERNAME = os.getenv("ZEPTO_SMTP_USERNAME")
ZEPTO_SMTP_PASSWORD = os.getenv("ZEPTO_SMTP_PASSWORD")
ZEPTO_FROM_ADDRESS = os.getenv("ZEPTO_FROM_ADDRESS")
ZEPTO_FROM_NAME = os.getenv("ZEPTO_FROM_NAME")


def send_email(to_email: str, to_name: str, subject: str, body_html: str, body_text: str = None) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{ZEPTO_FROM_NAME} <{ZEPTO_FROM_ADDRESS}>"
        msg["To"] = f"{to_name} <{to_email}>"

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        server = smtplib.SMTP("smtp.zeptomail.in", 587)
        server.starttls()
        server.login(ZEPTO_SMTP_USERNAME, ZEPTO_SMTP_PASSWORD)
        server.sendmail(ZEPTO_FROM_ADDRESS, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
