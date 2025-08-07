from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

registrationStatus = Table(
    "registrationStatus",
    metadata,
    Column("registrationStatusId", Integer, primary_key=True),
    Column("statusName", String(50))
)
