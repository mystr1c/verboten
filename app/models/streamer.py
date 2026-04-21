from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class StreamerORM(Base):
    __tablename__ = "streamers"

    username: Mapped[str] = mapped_column()
