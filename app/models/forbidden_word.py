from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

class ForbiddenWordORM(Base):
    __tablename__ = "forbidden_words"

    word_id: Mapped[int] = mapped_column(ForeignKey('words.id'))
    forbidden_word: Mapped[str]
