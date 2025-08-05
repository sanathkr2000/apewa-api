import sqlalchemy as sa
from app.db.database import metadata

departments = sa.Table(
    "departments", metadata,
    sa.Column("departmentId", sa.Integer, primary_key=True),
    sa.Column("departmentName", sa.String(100)),
    sa.Column("isActive", sa.Boolean),
)
