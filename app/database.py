from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

postgresql_database = "postgresql+psycopg2://habit_user:habit_password@localhost:5432/habit_tracker"
engine = create_engine(postgresql_database)

class Base(DeclarativeBase): 
    pass

def init_db() -> None:
    from app import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)