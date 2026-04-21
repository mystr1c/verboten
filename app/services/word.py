from app.models.word import WordORM
from app.models.forbidden_word import ForbiddenWordORM
from app.models.used_word import UsedWordORM
import random
from app.database import session_factory
from sqlalchemy import select, func

def get_word_from_db(game_id: int):
    with session_factory() as session:
        used_words = session.execute(select(UsedWordORM.word).where(UsedWordORM.game_id == game_id)).scalars().all()
        random_word = session.execute(select(WordORM).where(WordORM.word.not_in(used_words)).order_by(func.random()).limit(1)).scalar_one()
        forbidden_words = session.execute(select(ForbiddenWordORM.forbidden_word).where(ForbiddenWordORM.word_id == random_word.id)).scalars().all()

    return (random_word.word, forbidden_words)
