from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from backend.app.config import settings


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)