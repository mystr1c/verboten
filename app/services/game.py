from app.database import session_factory
from app.models.game import GameORM
from app.models.streamer import StreamerORM
from app.models.used_word import UsedWordORM
from app.models.leaderboard import LeaderboardORM
from app.models.enums import Status
from sqlalchemy import func, select

def insert_game(streamer_id, round_limit, time_limit):
    game = GameORM(
        streamer_id=streamer_id, 
        round_limit=round_limit, 
        time_limit=time_limit,
        status=Status.going
        )
    
    with session_factory() as session:
        session.add(game)
        session.commit()
        return game.id

def finish_game(game_id):
    with session_factory() as session:
        current_game = session.get(GameORM, game_id)
        if current_game:
            current_game.status = Status.finished
            current_game.finished_at = func.now()
            session.commit()

def find_game(streamer_login: str):
    with session_factory() as session:
        streamer_id = session.execute(select(StreamerORM.id).where(StreamerORM.username == streamer_login)).scalar_one()
        active_game = session.execute(select(GameORM).where(GameORM.streamer_id == streamer_id, GameORM.status == Status.going)).scalar_one_or_none()
        if active_game:
            used_words = session.execute(select(UsedWordORM).where(UsedWordORM.game_id == active_game.id).order_by(UsedWordORM.id)).scalars().all()
            current_round = len(used_words)
            if not used_words or used_words[-1].status == Status.finished:
                current_word = None
            else:
                current_word = used_words[-1].word
            
            leaderboard_people = session.execute(select(LeaderboardORM).where(LeaderboardORM.game_id == active_game.id)).scalars().all()
            leaderboard = {}
            for leaderboard_guy in leaderboard_people:
                leaderboard[leaderboard_guy.nickname] = leaderboard_guy.score

            return {
                "max_rounds": active_game.round_limit,
                "current_round": current_round, 
                "current_word": current_word, 
                "timer_limit": active_game.time_limit, 
                "game_id": active_game.id, 
                "leaderboard": leaderboard
            }
        
        return None
