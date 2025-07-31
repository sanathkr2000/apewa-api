from app.db.metadata import metadata  # ✅ Correct — your SQLAlchemy metadata
import databases
import sqlalchemy
from app.config import config



# connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else{}
engine = sqlalchemy.create_engine(
    config.DATABASE_URL, connect_args={}
)

metadata.create_all(engine)

db_args = {"min_size": 1, "max_size": 3} if "postgres" in config.DATABASE_URL else{}
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK, **db_args
)

