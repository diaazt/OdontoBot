from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import settings


DATABASE_URL = URL.create(              #crea la url de la base de datos
    drivername="postgresql+psycopg",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)


engine = create_engine(                 #crea el motor de la base de datos
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(            #crea la sesion de la base de datos
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):            #crea la base de datos
    pass

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()