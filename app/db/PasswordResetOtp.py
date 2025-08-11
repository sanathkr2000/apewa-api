# app/db/PasswordResetOtp.py
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey, MetaData
from app.db.database import metadata

passwordResetOtp = Table(
    "passwordResetOtp",
    metadata,
    Column("otpId", Integer, primary_key=True, autoincrement=True),
    Column("userId", Integer, ForeignKey("users.userId"), nullable=False),
    Column("otpCode", String(10), nullable=False),
    Column("expiryTime", DateTime, nullable=False),
    Column("isUsed", Boolean, default=False)
)
