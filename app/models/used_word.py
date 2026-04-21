from app.models.base import Base
from sqlalchemy import func, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.enums import Status

class UsedWordORM(Base):
    __tablename__ = 'used_words'
    
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    word: Mapped[str]
    status: Mapped[Status]
    finished_at: Mapped[datetime] = mapped_column(nullable=True)
