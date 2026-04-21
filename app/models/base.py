from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime
from sqlalchemy import func

class Base(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
