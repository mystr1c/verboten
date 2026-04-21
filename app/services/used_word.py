from app.models.used_word import UsedWordORM
from app.database import session_factory
from app.models.enums import Status
from sqlalchemy import select, func

def insert_used_word(game_id:int, word:str) -> None:
    with session_factory() as session:
        used_word = UsedWordORM(
            game_id=game_id,
            word=word,
            status=Status.going
        )
        session.add(used_word)
        session.commit()

def make_used_word_finished(game_id:int, word:str) -> None:
    with session_factory() as session:
        used_word = session.execute(select(UsedWordORM).filter_by(game_id=game_id, word=word)).scalar_one()
        used_word.status = Status.finished
        used_word.finished_at = func.now()
        session.commit()
