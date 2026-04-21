from app.models import Base
from sqlalchemy.orm import Mapped, mapped_column

class WordORM(Base):
    __tablename__ = 'words'

    word: Mapped[str]
