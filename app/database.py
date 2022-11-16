from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)

# (para uso de pruebas)
# Comentar la linea anterior y decomentar las siguientes 4líneas para uso de sqlite:

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@as_declarative()
class Base:

    # Definir el nombre de las tablas en base a el nombre de la clase
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
