from pydantic import BaseModel

class UpdateLeaderboardSchema(BaseModel):
    nickname: str