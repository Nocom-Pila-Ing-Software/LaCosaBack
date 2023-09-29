from pydantic import BaseModel

class PlayerName(BaseModel):
    playerName: str

class PlayerID(BaseModel):
    playerID: int
