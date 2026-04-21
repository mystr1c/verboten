from app.models.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class LeaderboardORM(Base):
    __tablename__ = "leaderboards"
    
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    nickname: Mapped[str] = mapped_column()
    score: Mapped[int] = mapped_column()
