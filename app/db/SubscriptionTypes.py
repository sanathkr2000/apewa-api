import sqlalchemy as sa
from app.db.database import metadata

subscriptionTypes = sa.Table(
    "subscriptionTypes", metadata,
    sa.Column("subscriptionTypeId", sa.Integer, primary_key=True),
    sa.Column("subscriptionTypeName", sa.String(100)),
    sa.Column("price", sa.Float),
    sa.Column("isActive", sa.Boolean),
)
