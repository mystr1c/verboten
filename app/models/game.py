from app.models.base import Base
from datetime import datetime
from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.enums import Status

class GameORM(Base):
    __tablename__ = "games"
    
    streamer_id: Mapped[int] = mapped_column(ForeignKey("streamers.id"))
    round_limit: Mapped[int]
    time_limit: Mapped[int]
    status: Mapped[Status]
    finished_at: Mapped[datetime] = mapped_column(nullable=True)
