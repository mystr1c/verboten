from app.models.leaderboard import LeaderboardORM
from app.database import session_factory
from sqlalchemy import select
from typing import TypedDict

class WinnerResult(TypedDict):
    nickname: str
    score: int

def add_points(game_id:int, nickname: str, score:int) -> WinnerResult:
    with session_factory() as session:
        winner = session.execute(select(LeaderboardORM).filter_by(game_id=game_id, nickname=nickname)).scalar_one_or_none()
        if winner:
            winner.score = winner.score + score
        else:
            winner = LeaderboardORM(game_id=game_id, nickname=nickname, score=score)
            session.add(winner)
        session.commit()
        return {'nickname': winner.nickname, 'score': winner.score}
