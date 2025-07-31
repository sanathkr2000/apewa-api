# users.py

# from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey, MetaData, func
# from app.db.metadata import metadata
#
# users = Table(
#     "users",
#     metadata,
#     Column("userId", Integer, primary_key=True, autoincrement=True),
#     Column("firstName", String(100), nullable=False),
#     Column("lastName", String(100), nullable=False),
#     Column("email", String(150), unique=True, nullable=False, index=True),
#     Column("password", String(255), nullable=False),
#     Column("phoneNumber", String(20)),
#     Column("departmentId", Integer, ForeignKey("departments.departmentId")),
#     Column("roleId", Integer, ForeignKey("roles.roleId")),
#     Column("subscriptionTypeId", Integer, ForeignKey("subscriptionTypes.subscriptionTypeId")),
#     Column("registrationStatus", Boolean, default=False),
#     Column("isActive", Boolean, default=True),
#     Column("createdAt", DateTime(timezone=True), server_default=func.now())
# )
#
#
# userPayments = Table(
#     "userPayments",
#     metadata,
#     Column("userPaymentId", Integer, primary_key=True, autoincrement=True),
#     Column("userId", Integer, ForeignKey("users.userId")),
#     Column("paymentEvidence", String(255)),
#     Column("transactionId", String(100)),
#     Column("isActive", Boolean, default=True),
#     Column("createdAt", DateTime(timezone=True), server_default=func.now())
# )


# users.py

import sqlalchemy as sa
from app.db.database import metadata

users = sa.Table(
    "users", metadata,
    sa.Column("userId", sa.Integer, primary_key=True),
    sa.Column("firstName", sa.String(100)),
    sa.Column("lastName", sa.String(100)),
    sa.Column("email", sa.String(150), unique=True),
    sa.Column("password", sa.String(255)),
    sa.Column("phoneNumber", sa.String(20)),
    sa.Column("departmentId", sa.Integer),
    sa.Column("roleId", sa.Integer),
    sa.Column("subscriptionTypeId", sa.Integer),
    sa.Column("registrationStatus", sa.Boolean, default=False),
    sa.Column("isActive", sa.Boolean, default=True),
    sa.Column("createdAt", sa.DateTime),
)

userPayments = sa.Table(
    "userPayments", metadata,
    sa.Column("userPaymentId", sa.Integer, primary_key=True),
    sa.Column("userId", sa.Integer),
    sa.Column("paymentEvidence", sa.String(255)),
    sa.Column("transactionId", sa.String(100)),
    sa.Column("isActive", sa.Boolean, default=True),
    sa.Column("createdAt", sa.DateTime),
)
