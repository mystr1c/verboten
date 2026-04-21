from app.models.streamer import StreamerORM
from app.database import session_factory
from sqlalchemy import select

def get_or_create_streamer(username:str) -> int:
    with session_factory() as session:
        streamer = session.execute(select(StreamerORM).filter_by(username=username)).one_or_none()
        if not streamer:
            streamer = StreamerORM(
                username=username
            )
            session.add(streamer)
        session.commit()
        return streamer.id
