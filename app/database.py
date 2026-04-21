from sqlalchemy import create_engine
from app.config import settings
from sqlalchemy.orm import sessionmaker
from app.models import Base

engine = create_engine(url=settings.DB_CONNECT, echo=True, pool_size=5, max_overflow=10)

session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=True)

def init_db():
    Base.metadata.create_all(bind=engine)
