from pydantic import BaseModel

class CreateGameSchema(BaseModel):
    round_limit: int
    time_limit: int

class UpdateGameSchema(BaseModel):
    status: str
    current_word: str | None = None